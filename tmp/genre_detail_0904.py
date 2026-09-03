# -*- coding: utf-8 -*-
import re, json, io

p = r"C:\Users\user\oshinavi\index.html"
s = io.open(p, encoding="utf-8", newline="").read()
arr = json.loads(re.search(r"const EVENTS = (\[.*?\]);", s, re.S).group(1))
want = [6397, 6395, 6404, 6477, 6429, 6430, 6437, 6442, 6435, 6416, 6402, 6405,
        6433, 6434, 6439, 6408, 6478, 6399, 6484, 6394]
out = io.open(r"C:\Users\user\oshinavi\tmp\genre_detail_0904.txt", "w", encoding="utf-8")
for e in arr:
    if e.get("id") in want:
        d = {k: v for k, v in e.items() if k in
             ("id", "name", "artist", "venue", "date", "dateLabel", "type",
              "_genre", "_piaSub", "_piaGenre", "description", "url", "officialUrl",
              "extraGenres", "area")}
        out.write(json.dumps(d, ensure_ascii=False, indent=1) + "\n---\n")
out.close()
print("ok")
