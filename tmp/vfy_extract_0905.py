import json, io, sys, re

SRC = r"C:\Users\user\oshinavi\index.html"
OUT = r"C:\Users\user\oshinavi\tmp\vfy_entries_0905.txt"

with io.open(SRC, encoding="utf-8") as f:
    lines = f.readlines()

# EVENTS array: from line with 'const EVENTS = [' to the line '];'
start = None
for i, l in enumerate(lines):
    if "const EVENTS = [" in l:
        start = i
        break
end = None
for i in range(start, len(lines)):
    if lines[i].rstrip("\r\n") == "];":
        end = i
        break

body = "".join(lines[start:end+1])
body = body[body.index("["):]
body = body[:body.rindex("]")+1]
EV = json.loads(body)
sys.stderr.write("total entries: %d\n" % len(EV))

TARGETS = [6935,6936,6937,6938,6939,6940,6941,6942,6943,6944,6945,6103,6295,6080,583]

byid = {e["id"]: e for e in EV}

out = []
for t in TARGETS:
    e = byid.get(t)
    if e is None:
        out.append("=== id %d : NOT FOUND ===" % t)
        continue
    out.append("=== id %d ===" % t)
    for k in ("artist","name","date","dateLabel","venue","prefecture","genre"):
        out.append("  %s: %s" % (k, e.get(k)))
    out.append("  links: %s" % json.dumps(e.get("links"), ensure_ascii=False))
    for i, tk in enumerate(e.get("tickets") or []):
        out.append("  ticket[%d]: type=%s | date=%s | startDate=%s | url=%s" % (
            i, tk.get("type"), tk.get("date"), tk.get("startDate"), tk.get("url")))
    out.append("")

# dump all urls for fetching
urls = []
for t in TARGETS:
    e = byid.get(t)
    if not e: continue
    for tk in (e.get("tickets") or []):
        u = tk.get("url")
        if u:
            urls.append((t, u))
    lk = e.get("links") or {}
    for k, v in lk.items():
        if v:
            urls.append((t, "LINK:%s:%s" % (k, v)))

with io.open(r"C:\Users\user\oshinavi\tmp\vfy_urls_0905.json", "w", encoding="utf-8") as f:
    json.dump(urls, f, ensure_ascii=False, indent=1)

# also dump full EVENTS to a json for later cross-checks
with io.open(r"C:\Users\user\oshinavi\tmp\vfy_all_events_0905.json", "w", encoding="utf-8") as f:
    json.dump(EV, f, ensure_ascii=False)

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("ok")
