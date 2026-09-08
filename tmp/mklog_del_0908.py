# -*- coding: utf-8 -*-
"""削除する15件の記録を作る。URLは index.html から機械抽出する（手で書かない・創作しない）。"""
import io, re, json

IDS = [16, 271, 858, 1833, 2430, 2773, 3936, 5698, 5712, 6177, 6183, 6184, 6234, 6265, 6545]

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = {e["id"]: e for e in json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))}

TODAY = "2026-09-08"

def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), t.get("date")
    return not ((not sd or sd <= TODAY) and (d or "") < TODAY)

out = io.open("logs/removed_2026-09-08.md", "w", encoding="utf-8")
W = out.write
W("# 2026-09-08 朝に削除したエントリ\n\n")
W("理由＝**公演が終わった**（OSHINAVIは買える公演のカウントダウン）。\n")
W("売り切れ・販売終了は削除していない（`soldout`で画面に残す決まり）。\n\n")
W("判定＝別エージェントの独立再検証で15件とも「削除OK・保留0件」。\n")
W("配信/視聴/オンライン券は15件とも該当なし＝公演後に生きる枠は無い。\n\n")
W("| id | 公演名 | 会場 | 公演日 | 画面に出ていた枠 | 確認用URL |\n|---|---|---|---|---|---|\n")

missing = []
for i in IDS:
    e = EV.get(i)
    if not e:
        missing.append(i)
        continue
    lk = e.get("links", {}) or {}
    url = (lk.get("pia") or lk.get("rakuten") or lk.get("eplus")
           or lk.get("lawson") or e.get("url") or "").strip()
    if not url:
        for t in e.get("tickets", []) or []:
            if (t.get("url") or "").strip():
                url = t["url"].strip()
                break
    nvis = sum(1 for t in (e.get("tickets") or []) if visible(t))
    label = "確認" if url else "(URLがデータに無い)"
    cell = "[%s](%s)" % (label, url) if url else "(URLがデータに無い)"
    W("| %d | %s | %s | %s | %d | %s |\n" % (
        i,
        (e.get("title") or e.get("name") or "").replace("|", "｜")[:44],
        (e.get("venue") or "").replace("|", "｜")[:30],
        e.get("date") or "",
        nvis, cell))
out.close()
print("wrote logs/removed_2026-09-08.md  rows=%d  missing=%s" % (len(IDS) - len(missing), missing))
