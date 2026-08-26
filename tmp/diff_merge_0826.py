# -*- coding: utf-8 -*-
"""統合の再導出で「消えるはずだった枠」を並べて見る。通信なし。
枠が減るのは①受付終了が落ちた（正常）②混雑ページを掴んで静かに消えた（事故）のどちらか。
見分けるために、消える枠の締切が過去か未来かを出す。"""
import json
import sys
import datetime

sys.stdout.reconfigure(encoding="utf-8")

TODAY = datetime.date.today().isoformat()
IDS = set(int(x) for x in sys.argv[1].split(","))
rows = json.load(open("tmp/merge_result_0826.json", encoding="utf-8"))

import re
src = open("index.html", encoding="utf-8").read()
m = re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S)
by_id = {e["id"]: e for e in json.loads(m.group(1))}

for r in rows:
    if r["id"] not in IDS:
        continue
    ev = by_id.get(r["id"])
    old = ev.get("tickets") or []
    new = r["tickets"]
    newset = {(t.get("type"), t.get("date")) for t in new}
    gone = [t for t in old if (t.get("type"), t.get("date")) not in newset]
    print("=" * 72)
    print("id=%d %s （%d枠 → %d枠）" % (r["id"], r.get("artist"), len(old), len(new)))
    print("  URL: %s" % " ".join(r["urls"]))
    print("  --- 消えるはずだった枠 %d ---" % len(gone))
    for t in gone:
        d = t.get("date") or ""
        mark = "🚨まだ未来＝生きてるかも" if d > TODAY else "✅締切が過ぎている"
        print("    %s | date=%s %s" % (t.get("type"), d, mark))
    print("  --- 再導出で出た枠 %d ---" % len(new))
    for t in new:
        print("    %s | date=%s" % (t.get("type"), t.get("date")))
    print("")
