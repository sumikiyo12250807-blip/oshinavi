# -*- coding: utf-8 -*-
"""スイープの未掲載候補64件を build_pia_entries の入力形式にする。
newid は現物の最大id+1 から連番（新着プールの並びは投入順＝id昇順で固定）。
"""
import io, re, json, glob, os

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
nid = max(e["id"] for e in EV) + 1

# 既に登録してあるぴあの eventCd を全部集める（links.pia と各 ticket.url の両方）
have = set()
for e in EV:
    for u in [(e.get("links") or {}).get("pia")] + [t.get("url") for t in e.get("tickets", [])]:
        if u:
            for m in re.finditer(r"event(?:Bundle)?Cd=([a-zA-Z0-9]+)", u):
                have.add(m.group(1))

seen, cand, dup = set(), [], []
for p in sorted(glob.glob("tmp/presale_0907_*.json")):
    d = json.load(io.open(p, encoding="utf-8"))
    for c in d.get("new") or []:
        url = c.get("url") or ""
        m = re.search(r"event(?:Bundle)?Cd=([a-zA-Z0-9]+)", url)
        cd = m.group(1) if m else url
        if cd in seen:
            continue
        seen.add(cd)
        if cd in have:          # 投入済みのeventCdは足さない（二重登録の防止）
            dup.append((cd, c.get("artist")))
            continue
        cand.append({"newid": nid, "artist": c.get("artist") or "",
                     "urls": [url], "_src": os.path.basename(p),
                     "_rls": c.get("rlsdate"), "_perf": c.get("perfdate"),
                     "_venue": c.get("venue")})
        nid += 1

json.dump([{k: v for k, v in c.items() if not k.startswith("_")} for c in cand],
          io.open("tmp/cand_0907.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

with io.open("tmp/cand_0907.txt", "w", encoding="utf-8") as f:
    f.write("=== 投入候補 %d件（id %s..%s）===\n" % (len(cand), cand[0]["newid"], cand[-1]["newid"]) if cand else "候補なし\n")
    for c in cand:
        f.write("  id=%-6s 発売%-11s %-30s %s\n     %s\n"
                % (c["newid"], c["_rls"] or "-", (c["artist"] or "")[:30],
                   (c["_venue"] or "")[:34], c["urls"][0]))
    if dup:
        f.write("\n=== 既にeventCdが登録済みなので足さない %d件 ===\n" % len(dup))
        for cd, a in dup:
            f.write("  %s %s\n" % (cd, a))

print("候補 %d件 / 既登録で除外 %d件" % (len(cand), len(dup)))
