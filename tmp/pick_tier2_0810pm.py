# -*- coding: utf-8 -*-
"""第2優先群（演劇=お笑い含む／クラシック）から不足分を足す。
ユーザー指示 2026-08-10夜の優先順＝①音楽全般（J-POP最優先） ②演劇・ジャズ・クラシック・お笑い ③その他。
音楽(lg=01)は全部拾い切ったので、ここは lg=02(演劇・寄席お笑い) と lg=07(クラシック) から。
"""
import glob, json, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NEED = int(sys.argv[1]) if len(sys.argv) > 1 else 7
FAR = "2026-08-14"
TIER2 = ("02", "07")

src = open("index.html", "rb").read().decode("utf-8")
have = set(re.findall(r"event(?:Bundle)?Cd=([0-9a-zA-Z]+)", src))
used_urls = set()
for p in ("tmp/cand_music_0810pm.json",):
    for c in json.load(open(p, encoding="utf-8")):
        used_urls |= set(c["urls"])
built = json.load(open("tmp/built_music_0810pm.json", encoding="utf-8"))
nextid = max(e["id"] for e in built) + 1

rows, seen = [], set()
for p in sorted(glob.glob("tmp/presale_*_0810pm.json")):
    lg = re.search(r"presale_(\d\d)_", p).group(1)
    if lg not in TIER2:
        continue
    for r in json.load(open(p, encoding="utf-8"))["new"]:
        m = re.search(r"event(?:Bundle)?Cd=([0-9a-zA-Z]+)", r["url"])
        cd = m.group(1) if m else ""
        if not cd or cd in seen or cd in have or r["url"] in used_urls:
            continue
        seen.add(cd)
        rows.append(r)


def ymd(s):
    m = re.match(r"(\d{4})/(\d{1,2})/(\d{1,2})", s or "")
    return "%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3))) if m else ""


far = sorted([r for r in rows if ymd(r.get("rlsdate")) >= FAR], key=lambda r: ymd(r["rlsdate"]))
near = sorted([r for r in rows if ymd(r.get("rlsdate")) < FAR],
              key=lambda r: (ymd(r.get("rlsdate")) or "9999", ymd(r.get("perfdate"))))

order, groups = [], {}
for r in far + near:
    a = r["artist"]
    if a not in groups:
        groups[a] = []
        order.append(a)
    groups[a].append(r)

out = []
for a in order[:NEED]:
    out.append({"newid": nextid + len(out), "artist": a, "urls": [x["url"] for x in groups[a]]})

json.dump(out, open("tmp/cand_tier2_0810pm.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("第2優先群の候補 %d件 → %dエントリ選定（id %d〜）" % (len(rows), len(out), nextid))
for c in out:
    print("  %d %s (%d本)" % (c["newid"], c["artist"], len(c["urls"])))
