# -*- coding: utf-8 -*-
"""記事に載せていない組を「この窓で発売する枠数」の多い順に並べる。
記事の基準＝①大物 ②今週まとめて一斉発売になるアーティスト（枠数が多い）なので、
枠数で並べると「一斉発売なのに落ちている組」が上に来る。
"""
import io, re, json

FROM, TO = "2026-09-07", "2026-09-13"

bs = io.open("tmp/pickup0906/build_section.py", encoding="utf-8").read()
mm = re.search(r"MAIN = \[(.*?)\]\n", bs, re.S)
tt = re.search(r"TILES = \[(.*?)\]\n", bs, re.S)
in_article = set(int(x) for x in re.findall(r",\s*(\d+)\)", mm.group(1) + tt.group(1)))

html = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))

rows = []
for e in EV:
    n = 0
    for t in e.get("tickets", []):
        sd = t.get("startDate")
        if sd and FROM <= sd <= TO:
            n += 1
    if n:
        rows.append((n, e["id"], e.get("artist") or e.get("name", ""), e.get("genre"),
                     (e.get("venue") or "")[:34], e["id"] in in_article))

rows.sort(key=lambda r: (-r[0], r[1]))

with open("tmp/gap_rank_0907.txt", "w", encoding="utf-8") as f:
    f.write("=== この窓(%s〜%s)で発売が始まる枠が多い順・上位60 ===\n" % (FROM, TO))
    f.write("★=記事に載せている組\n\n")
    for r in rows[:60]:
        f.write("  %s %2d枠  id=%-5s %-28s [%-9s] %s\n"
                % ("★" if r[5] else "  ", r[0], r[1], r[2][:28], r[3], r[4]))
    f.write("\n=== 記事に載せていない組だけ・上位40 ===\n")
    k = 0
    for r in rows:
        if r[5]:
            continue
        k += 1
        if k > 40:
            break
        f.write("  %2d枠  id=%-5s %-28s [%-9s] %s\n" % (r[0], r[1], r[2][:28], r[3], r[4]))
print("窓に枠がある %d件 / 記事に載せた %d件" % (len(rows), sum(1 for r in rows if r[5])))
