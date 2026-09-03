# -*- coding: utf-8 -*-
import re, json, subprocess, io

ids = [1782, 2072, 2359, 2630, 2631, 6192]
revs = ["HEAD", "HEAD~1", "HEAD~2", "HEAD~3", "HEAD~5", "HEAD~8"]
out = io.open(r"C:\Users\user\oshinavi\tmp\hist6_out.txt", "w", encoding="utf-8")
for rev in revs:
    try:
        raw = subprocess.check_output(["git", "show", "%s:index.html" % rev],
                                      cwd=r"C:\Users\user\oshinavi")
    except Exception as ex:
        out.write("%s ERROR %r\n" % (rev, ex))
        continue
    src = raw.decode("utf-8", "replace")
    m = re.search(r"const EVENTS = (\[.*?\]);", src, re.S)
    if not m:
        out.write("%s: EVENTS not found\n" % rev)
        continue
    ev = json.loads(m.group(1))
    d = {e["id"]: e for e in ev if e.get("id") in ids}
    out.write("=== %s\n" % rev)
    for i in ids:
        e = d.get(i)
        if not e:
            out.write("  %s: ABSENT\n" % i)
            continue
        ts = e.get("tickets", [])
        out.write("  %s: date=%s tickets=%d\n" % (i, e.get("date"), len(ts)))
        for t in ts:
            out.write("      %s | date=%s start=%s soldout=%s\n" % (
                t.get("type"), t.get("date"), t.get("startDate"), t.get("soldout")))
    out.write("\n")
out.close()
print("ok")
