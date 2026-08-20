import json, re, io

TODAY = "2026-08-06"
src = open("index.html", "rb").read().decode("utf-8")
m = re.search(r"  const EVENTS = (\[.*?\]);", src, re.S)
data = json.loads(m.group(1))

rows = []
for e in data:
    for t in e.get("tickets") or []:
        sd, d = t.get("startDate"), t.get("date")
        if sd and d and sd == d and d <= TODAY:
            rows.append((e["id"], e.get("artist", "")[:20], d, t.get("type", "")[:60]))

for r in sorted(rows):
    print(r[0], r[1], "|", r[2], "|", r[3])
print("計", len(rows), "枠 / today =", TODAY)
