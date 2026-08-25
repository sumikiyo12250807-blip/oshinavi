# -*- coding: utf-8 -*-
import json, os, time, urllib.request, re, sys

BASE = r"C:/Users/user/oshinavi"
IN = os.path.join(BASE, "tmp/genre_in_0825.json")
OUTDIR = os.path.join(BASE, "tmp")
items = json.load(open(IN, encoding="utf-8"))

log = open(os.path.join(OUTDIR, "g_fetch_log.txt"), "w", encoding="utf-8")
n_new = 0
for it in items:
    i = it["id"]; url = it["pia"]
    fp = os.path.join(OUTDIR, "g_%s.html" % i)
    if os.path.exists(fp) and os.path.getsize(fp) > 2000:
        continue
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        data = urllib.request.urlopen(req, timeout=40).read()
        open(fp, "wb").write(data)
        log.write("OK %s %s bytes\n" % (i, len(data)))
    except Exception as e:
        log.write("ERR %s %r\n" % (i, e))
    log.flush()
    n_new += 1
    time.sleep(1.8)
log.write("fetched=%d\n" % n_new)
log.close()
print("done", n_new)
