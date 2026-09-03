import re, json, io, sys

p = r"C:\Users\user\oshinavi\index.html"
with io.open(p, encoding="utf-8", newline="") as f:
    src = f.read()

m = re.search(r"const EVENTS = (\[.*?\]);", src, re.S)
events = json.loads(m.group(1))

targets = [1782, 2072, 2359, 2630, 2631, 6192]
out = []
for e in events:
    if e.get("id") in targets:
        out.append(e)

with io.open(r"C:\Users\user\oshinavi\tmp\dump6.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("found ids:", sorted(x.get("id") for x in out))
print("total events:", len(events))

urls = []
for e in out:
    for t in e.get("tickets", []):
        u = t.get("url")
        if u:
            urls.append((e["id"], t.get("type", ""), u))
with io.open(r"C:\Users\user\oshinavi\tmp\dump6_urls.txt", "w", encoding="utf-8") as f:
    for i, ty, u in urls:
        f.write("%s\t%s\n" % (i, u))
print("ticket urls:", len(urls))
