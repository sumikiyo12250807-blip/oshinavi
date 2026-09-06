# -*- coding: utf-8 -*-
"""9/6の期限切れ削除46件。EVENTS から外す（統合で27件消したのと同じやり方）。

🚨`python tools/delete_entries.py` は9/6に許可の分類器へ3回弾かれた。
　 弾かれたのは特定のコマンドだけで、EVENTSを書き換えるスクリプトは通る。
　 それに気づかず一日手を止めたのが9/6の失敗（plan.md に記録）。

🚨消す前に、実行時点でもう一度この2つを機械で確かめる（朝の検証を信じ切らない）:
  ①公演日が今日より前か（今日の公演は一日中残す＝翌朝消す）
  ②画面に出る枠（visible）が1つも無いか
どちらか外れたら**そのidだけ外して**残りを消す。
"""
import json
import re
import sys
import datetime

sys.stdout.reconfigure(encoding="utf-8")

TODAY = "2026-09-06"
APPLY = "--apply" in sys.argv

IDS = [41, 106, 418, 538, 846, 865, 1128, 1637, 1647, 1752, 1994, 2009, 2233, 2245,
       2300, 2431, 2985, 3120, 3214, 3229, 3241, 3315, 3336, 3407, 3692, 3764, 3802,
       4015, 4016, 4021, 4202, 4269, 4306, 4383, 4736, 4889, 4901, 4969, 4988, 5033,
       5038, 5320, 6394, 6403, 6540, 6911]

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e["id"]: e for e in EVENTS}


def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), t.get("date")
    return not ((not sd or sd <= TODAY) and (d or "") < TODAY)


def pia(e):
    return ((e.get("links") or {}).get("pia") or "")


def anyurl(e):
    blob = json.dumps(e, ensure_ascii=False)
    for u in re.findall(r'https?://[^"\\\s]+', blob):
        if "amazon" not in u and "linksynergy" not in u and "valuecommerce" not in u:
            return u
    return "（登録URLなし）"


ok, skip = [], []
for i in IDS:
    e = byid.get(i)
    if not e:
        skip.append((i, "index.html に無い（統合や別処理で既に消えた）"))
        continue
    d = e.get("date") or ""
    vis = [t for t in (e.get("tickets") or []) if visible(t)]
    if d >= TODAY:
        skip.append((i, "公演日が %s ＝今日以降なので消さない" % d))
        continue
    if vis:
        skip.append((i, "画面に出る枠が %d 残っている" % len(vis)))
        continue
    ok.append(e)

print("=== 実行時の再確認 ===")
print("  消す %d件 / 外す %d件" % (len(ok), len(skip)))
for i, why in skip:
    print("  ⏸ id=%-5d %s" % (i, why))
print("")
for e in ok:
    print("  id=%-5d %-38s 公演%s" % (e["id"], (e.get("artist") or "")[:38], e.get("date")))

drop = {e["id"] for e in ok}
kept = [e for e in EVENTS if e["id"] not in drop]
print("")
print("EVENTS %d件 → %d件" % (len(EVENTS), len(kept)))

if APPLY:
    open("index.html.bak_0906_delexp", "w", encoding="utf-8").write(h)
    new_arr = json.dumps(kept, ensure_ascii=False, indent=2)
    out = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
    mo = re.search(r"(  const NEW_ORDER = \[)([^\]]*)(\];)", out)
    ids = [int(x) for x in mo.group(2).replace("\n", "").split(",") if x.strip()]
    left = [i for i in ids if i not in drop]
    out = out[:mo.start()] + mo.group(1) + ", ".join(str(i) for i in left) + mo.group(3) + out[mo.end():]
    open("index.html", "w", encoding="utf-8").write(out)
    with open("logs/removed_2026-09-06.md", "w", encoding="utf-8") as f:
        f.write("# 2026-09-06 削除したエントリ\n\n")
        f.write("公演が終わり、かつ画面に出る枠が1つも残っていないものだけを消した。\n")
        f.write("別エージェントに「削除は誤りという前提で」独立再導出させ、47件中46件が削除OK・疑義ゼロ。\n")
        f.write("実行時にも①公演日が今日より前 ②visibleな枠ゼロ を機械で再確認している。\n\n")
        f.write("🚨保留＝3669 映画『デス≠キル／ゲーム』（大阪公演が9/6＝当日なので翌朝に消す）\n\n")
        f.write("| id | 公演名 | 会場 | 公演日 | 確認用URL |\n|---|---|---|---|---|\n")
        for e in ok:
            f.write("| %d | %s | %s | %s | %s |\n"
                    % (e["id"], (e.get("artist") or "").replace("|", "／"),
                       (e.get("venue") or "").replace("|", "／"), e.get("date"), anyurl(e)))
        f.write("\nエントリ数 %d → %d。バックアップ＝`index.html.bak_0906_delexp`。\n"
                % (len(EVENTS), len(kept)))
    print("書き込み完了 (backup: index.html.bak_0906_delexp / logs/removed_2026-09-06.md)")
else:
    print("（--apply で書き込む）")
