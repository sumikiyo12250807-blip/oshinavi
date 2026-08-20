import json, re, sys

src = open("index.html", "rb").read().decode("utf-8")
m = re.search(r"  const EVENTS = (\[.*?\]);", src, re.S)
data = json.loads(m.group(1))
ids = [int(x) for x in sys.argv[1].split(",")]
for e in data:
    if e["id"] in ids:
        print("=== id", e["id"], e.get("artist"), "|", e.get("venue"), "|", e.get("prefecture"), "| date", e.get("date"))
        print("  links:", json.dumps(e.get("links"), ensure_ascii=False))
        for t in e.get("tickets") or []:
            print("  -", json.dumps(t, ensure_ascii=False))
