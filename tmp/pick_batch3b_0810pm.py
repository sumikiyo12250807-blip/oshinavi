# -*- coding: utf-8 -*-
"""第3バッチの追い足し：売切で2件skipしたぶんを、次の候補から3公演だけ補う。"""
import glob, json, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ADD = 3
FAR = "2026-08-14"

src = open("index.html", "rb").read().decode("utf-8")
have = set(re.findall(r"event(?:Bundle)?Cd=([0-9a-zA-Z]+)", src))
done = json.load(open("tmp/cand3_0810pm.json", encoding="utf-8"))
done_urls = set(u for c in done for u in c["urls"])
done_artists = set(c["artist"] for c in done)
built = json.load(open("tmp/built3_0810pm.json", encoding="utf-8"))
nextid = max(e["id"] for e in built) + 1

rows, seen = [], set()
for p in sorted(glob.glob("tmp/presale_*_0810pm.json")):
    for r in json.load(open(p, encoding="utf-8"))["new"]:
        m = re.search(r"event(?:Bundle)?Cd=([0-9a-zA-Z]+)", r["url"])
        cd = m.group(1) if m else ""
        if not cd or cd in seen or cd in have or r["url"] in done_urls:
            continue
        if r["artist"] in done_artists:
            continue
        seen.add(cd)
        rows.append(r)


def ymd(s):
    m = re.match(r"(\d{4})/(\d{1,2})/(\d{1,2})", s or "")
    return "%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3))) if m else ""


far = sorted([r for r in rows if ymd(r.get("rlsdate")) >= FAR], key=lambda r: ymd(r["rlsdate"]))
near = sorted([r for r in rows if ymd(r.get("rlsdate")) < FAR],
              key=lambda r: (ymd(r.get("rlsdate")) or "9999", ymd(r.get("perfdate"))))

out, used = [], 0
for r in far + near:
    if used >= ADD:
        break
    out.append({"newid": nextid + len(out), "artist": r["artist"], "urls": [r["url"]]})
    used += 1

json.dump(out, open("tmp/cand3b_0810pm.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("追い足し %d件（id %d〜）" % (len(out), nextid))
for c in out:
    print("  %d %s" % (c["newid"], c["artist"]))
