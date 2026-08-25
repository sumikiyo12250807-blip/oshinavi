# -*- coding: utf-8 -*-
import json, os, re
BASE = r"C:/Users/user/oshinavi"
items = json.load(open(os.path.join(BASE,"tmp/genre_in_0825.json"), encoding="utf-8"))
out = {}
for it in items:
    i = str(it["id"])
    fp = os.path.join(BASE, "tmp", "g_%s.html" % i)
    raw = open(fp, "rb").read()
    html = raw.decode("utf-8", "replace")
    t = re.search(r"<title>(.*?)</title>", html, re.S)
    title = t.group(1).strip() if t else ""
    # subgenre from title: [XXX のチケット購入・予約]
    sub = None
    m = re.search(r"\[([^\[\]]+?)のチケット", title)
    if m: sub = m.group(1)
    gcds = re.findall(r'genreCd"?\s+value="(\d+)"', html)
    gcds2 = re.findall(r'name="genreCd"\s+value="(\d+)"', html)
    allg = sorted(set(gcds + gcds2))
    # also look for any genreCd occurrence
    anyg = sorted(set(re.findall(r'genreCd[^0-9]{0,20}(\d{5,9})', html)))
    out[i] = {"name": it["name"], "url": it["pia"], "title": title, "sub": sub,
              "genreCd": allg, "genreCdAny": anyg}
json.dump(out, open(os.path.join(BASE,"tmp/g_extract.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("done", len(out))
