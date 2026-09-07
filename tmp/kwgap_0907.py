# -*- coding: utf-8 -*-
"""pia_kw_search の結果と登録データを突き合わせて、未登録の eventCd を炙り出す。

🚨 ツアーの bundle ページだけ見ていると、そこに出てこない公演を落とす
   （feedback_pia_bundle_hides_shows＝来生たかお 2枠→5枠）。
   だから**アーティスト名で引いた全ヒット**と、登録済みの eventCd を突き合わせる。

使い方: python tmp/kwgap_0907.py <kw結果.txt> <このアーティストの登録id...>
"""
import io, re, json, sys

src = io.open(sys.argv[1], encoding="utf-8").read()
ids = [int(x) for x in sys.argv[2:]]

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))

# 登録済みの eventCd を全部集める（links.pia と各 ticket.url の両方）
have = set()
for e in EV:
    for u in [(e.get("links") or {}).get("pia")] + [t.get("url") for t in e.get("tickets", [])]:
        if u:
            for m in re.finditer(r"event(?:Bundle)?Cd=([a-zA-Z0-9]+)", u):
                have.add(m.group(1))

# kw結果をブロックに割る
blocks = re.split(r"\n(?=\[)", src)
rows = []
for b in blocks:
    m = re.search(r"URL   : (\S+)", b)
    if not m:
        continue
    cd = re.search(r"event(?:Bundle)?Cd=([a-zA-Z0-9]+)", m.group(1))
    if not cd:
        continue
    name = b.split("\n")[0].strip()
    date = (re.search(r"公演日: (.*)", b) or [None, "-"])[1]
    ven = (re.search(r"会場  : (.*)", b) or [None, "-"])[1]
    rows.append((cd.group(1), cd.group(1) in have, name[:52], date.strip()[:40], ven.strip()[:44], m.group(1)))

out = io.open("tmp/kwgap_0907.txt", "a", encoding="utf-8")
out.write("\n=== %s ===\n" % sys.argv[1])
miss = [r for r in rows if not r[1]]
out.write("ヒット %d件 / うち未登録 %d件\n" % (len(rows), len(miss)))
for r in miss:
    out.write("  🚨未登録 %s\n     %s\n     %s ／ %s\n     %s\n" % (r[0], r[2], r[3], r[4], r[5]))
out.close()
print("%s: ヒット%d / 未登録%d" % (sys.argv[1].split("/")[-1], len(rows), len(miss)))
