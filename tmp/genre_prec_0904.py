# -*- coding: utf-8 -*-
import re, json, io
s = io.open(r"C:\Users\user\oshinavi\index.html", encoding="utf-8", newline="").read()
arr = json.loads(re.search(r"const EVENTS = (\[.*?\]);", s, re.S).group(1))
out = io.open(r"C:\Users\user\oshinavi\tmp\genre_prec_0904.txt", "w", encoding="utf-8")
subs = ["イベントその他", "講演会・トークショー", "映画祭", "洋画", "邦画",
        "スクール・レジャー", "祭り・花火大会", "演歌・邦楽", "民族音楽", "フェスティバル"]
for e in arr:
    if e.get("genre") == "new":
        continue
    ps = e.get("_piaSub") or ""
    if any(x in ps for x in subs):
        out.write("%s | %s | %s\n" % (e.get("genre"), ps, e.get("name")))
out.write("\n=== genre counts for musicetc/talkshow/kids in site ===\n")
import collections
c = collections.Counter()
for e in arr:
    if e.get("genre") in ("musicetc", "talkshow", "kids", "enka", "hougaku", "kpop", "yougaku"):
        c[e["genre"]] += 1
out.write(str(dict(c)) + "\n")
out.write("\n=== enka entries (site) sample ===\n")
n = 0
for e in arr:
    if e.get("genre") == "enka" and n < 25:
        out.write("%s | piaSub=%s\n" % (e.get("name"), e.get("_piaSub")))
        n += 1
out.write("\n=== hougaku entries (site) sample ===\n")
n = 0
for e in arr:
    if e.get("genre") == "hougaku" and n < 25:
        out.write("%s | piaSub=%s\n" % (e.get("name"), e.get("_piaSub")))
        n += 1
out.close()
print("ok")
