# -*- coding: utf-8 -*-
import re, json, io, sys, collections

p = r"C:\Users\user\oshinavi\index.html"
s = io.open(p, encoding="utf-8", newline="").read()
m = re.search(r"const EVENTS = (\[.*?\]);", s, re.S)
arr = json.loads(m.group(1))
print("TOTAL_EVENTS", len(arr))

pool = [e for e in arr if e.get("genre") == "new"]
print("POOL", len(pool))

out = io.open(r"C:\Users\user\oshinavi\tmp\genre_pool_0904.txt", "w", encoding="utf-8")
def w(x):
    out.write(x + "\n")

w("=== POOL LIST (id / _genre / _piaSub / name) ===")
for i, e in enumerate(pool, 1):
    w("%3d | id=%s | _genre=%s | _piaSub=%s | %s" % (
        i, e.get("id"), e.get("_genre"), e.get("_piaSub"), e.get("name")))
    if e.get("extraGenres"):
        w("      extraGenres=%s" % (e.get("extraGenres"),))

w("")
w("=== _piaSub -> _genre MAP ===")
mp = collections.defaultdict(lambda: collections.defaultdict(list))
for e in pool:
    mp[e.get("_piaSub")][e.get("_genre")].append(e.get("id"))
for sub in sorted(mp.keys(), key=lambda x: (x is None, x)):
    gs = mp[sub]
    flag = "  <<< INCONSISTENT" if len(gs) > 1 else ""
    w("piaSub=%s -> %d genre(s)%s" % (sub, len(gs), flag))
    for g, ids in gs.items():
        w("    %s : n=%d ids=%s" % (g, len(ids), ids))

w("")
w("=== MISSING FIELDS ===")
for e in pool:
    miss = [k for k in ("_genre", "_piaSub") if not e.get(k)]
    if miss:
        w("id=%s missing=%s name=%s" % (e.get("id"), miss, e.get("name")))

w("")
w("=== GENRE COUNTS IN POOL ===")
c = collections.Counter(e.get("_genre") for e in pool)
for g, n in c.most_common():
    w("%s : %d" % (g, n))

w("")
w("=== SITE-WIDE piaSub->genre (non-new entries, for reference) ===")
mp2 = collections.defaultdict(lambda: collections.Counter())
for e in arr:
    if e.get("genre") == "new":
        continue
    if e.get("_piaSub"):
        mp2[e["_piaSub"]][e.get("genre")] += 1
for sub in sorted(mp2.keys()):
    w("piaSub=%s -> %s" % (sub, dict(mp2[sub])))

out.close()
print("written")
