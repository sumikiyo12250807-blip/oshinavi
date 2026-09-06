# -*- coding: utf-8 -*-
# 新着プールのぴあ由来エントリを抽出して、判定材料をファイルに書き出す
import io, re, json

h = io.open("C:/Users/user/oshinavi/index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
pool = [e for e in EV if e.get("genre") == "new" and (e.get("links") or {}).get("pia")]

out = []
out.append("count=%d" % len(pool))
for e in pool:
    out.append("----")
    out.append("id=%s" % e.get("id"))
    out.append("name=%s" % e.get("name"))
    out.append("artist=%s" % e.get("artist"))
    out.append("venue=%s" % e.get("venue"))
    out.append("piaSub=%s" % e.get("_piaSub"))
    out.append("date=%s" % e.get("date"))
    out.append("desc=%s" % (e.get("description") or "")[:200])
    out.append("pia=%s" % (e.get("links") or {}).get("pia"))

io.open("C:/Users/user/oshinavi/tmp/agent_genre_src_0907.txt", "w", encoding="utf-8").write("\n".join(out))

# piaSub の集計も出す
from collections import Counter
c = Counter([e.get("_piaSub") for e in pool])
io.open("C:/Users/user/oshinavi/tmp/agent_genre_subcount_0907.txt", "w", encoding="utf-8").write(
    "\n".join("%s\t%d" % (k, v) for k, v in sorted(c.items(), key=lambda x: -x[1]))
)
print("ok", len(pool))
