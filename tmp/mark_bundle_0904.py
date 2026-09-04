# -*- coding: utf-8 -*-
"""同じ枠に「個別ページ版」と「ツアーまとめページ版」の2枚のバッジが並んでいる箇所で、
まとめページ側の券種名に「・他の日程も見る」を書き足して区別できるようにする。

ユーザー指示 2026-09-04
> 「まったく同じ文字のボタンが2枚。これは何が違うの？
>   違うところを書いてボタンを2つのままにした方がいい」

実ページで確かめた違い（id505 石若駿トリオ）＝
  個別 eventCd=2618035        … 新潟10/18の1公演だけ
  まとめ eventBundleCd=b2670733 … 3公演の一覧（茨城10/17・新潟10/18・埼玉2027/1/31）
→ まとめページの価値は「**他の日程も選べる**」こと。だから2枚とも残して、押した結果を書く。

🚨書き足す場所は**券種名の括弧の中**。括弧の外に出すと renderCard の発売時刻抽出
   （「最後の閉じ括弧より後ろ」を見る）が壊れる＝[[feedback_tour_consolidate]]の2026-08-30項。

  python tmp/mark_bundle_0904.py          # 下見
  python tmp/mark_bundle_0904.py --apply  # 実行
"""
import json, re, io, sys, shutil
from collections import defaultdict

PATH = "index.html"
MARK = "・他の日程も見る"
APPLY = "--apply" in sys.argv

raw = io.open(PATH, encoding="utf-8", newline="").read()
m = re.search(r"const EVENTS = (\[.*?\]);\r?\n", raw, re.S)
src_text = m.group(1)
events = json.loads(src_text)


def dump(evs):
    return json.dumps(evs, ensure_ascii=False, indent=2)


if dump(events) != src_text.replace("\r\n", "\n"):
    print("ABORT: 書式の往復チェックに落ちた"); sys.exit(1)

n, skipped = 0, []
rows = []
for e in events:
    g = defaultdict(list)
    for t in e.get("tickets", []):
        g[(t.get("type"), t.get("date"))].append(t)
    for k, ts in g.items():
        if len(ts) < 2:
            continue
        urls = set((t.get("url") or "") for t in ts)
        if len(urls) < 2 or "" in urls:
            continue                                  # A/B型はここでは扱わない
        bund = [t for t in ts if "eventBundleCd=" in (t.get("url") or "")]
        indiv = [t for t in ts if t.get("url") and "eventBundleCd=" not in t.get("url")]
        if not bund or not indiv or len(bund) + len(indiv) != len(ts):
            skipped.append((e.get("id"), k[0], "個別とまとめの組み合わせでない")); continue
        for t in bund:
            ty = t.get("type") or ""
            if MARK in ty:
                continue
            # 券種名の「（… 公演）」の閉じ括弧の直前に書き足す
            new_ty, cnt = re.subn(r"（([^）]*公演)）", "（\\1%s）" % MARK, ty, count=1)
            if cnt != 1:
                skipped.append((e.get("id"), ty, "（…公演）の形でないので触らない")); continue
            rows.append((e.get("id"), e.get("name"), ty, new_ty))
            t["type"] = new_ty
            n += 1

print("書き足した枠=%d" % n)
print("触らなかった=%d" % len(skipped))
buf = ["まとめページ側のバッジに「%s」を書き足した 2026-09-04" % MARK, ""]
for eid, name, old, new in rows:
    buf.append("- id%s %s" % (eid, name))
    buf.append("    %s" % old)
    buf.append(" -> %s" % new)
buf.append("")
buf.append("【触らなかった】")
for eid, ty, why in skipped:
    buf.append("  id%s %s … %s" % (eid, ty[:50], why))
io.open("tmp/mark_bundle_0904.txt", "w", encoding="utf-8").write("\n".join(buf))

if not APPLY:
    print("(下見のみ。--apply で書き込み)  詳細 -> tmp/mark_bundle_0904.txt"); sys.exit(0)

shutil.copy(PATH, PATH + ".bak_0904_bundlemark")
out = raw[:m.start(1)] + dump(events).replace("\n", "\r\n") + raw[m.end(1):]
io.open(PATH, "w", encoding="utf-8", newline="").write(out)
print("WROTE index.html")
