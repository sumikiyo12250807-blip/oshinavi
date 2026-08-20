# -*- coding: utf-8 -*-
import re, sys, time, urllib.request, io

OUTP = sys.argv[1]
URLS = sys.argv[2:]
OUT = io.open(OUTP, "w", encoding="utf-8")
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
       "Accept-Language": "ja,en;q=0.8"}


def strip_tags(h):
    h = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?s)<[^>]+>", "\n", h)
    h = h.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return "\n".join([x.strip() for x in h.split("\n") if x.strip()])


for u in URLS:
    OUT.write("=" * 70 + "\n" + u + "\n")
    try:
        req = urllib.request.Request(u, headers=HDR)
        with urllib.request.urlopen(req, timeout=60) as r:
            html = r.read().decode("utf-8", "replace")
    except Exception as e:
        OUT.write("FETCH ERROR " + str(e) + "\n")
        OUT.flush()
        continue
    t = strip_tags(html)
    a = t.find("SHARE")
    b = t.find("スマチケ\nスマホから申し込むと")
    if a < 0:
        a = 0
    if b < 0:
        b = a + 4000
    OUT.write("len=%d\n" % len(html))
    OUT.write(t[max(0, a - 900):b] + "\n")
    OUT.flush()
    time.sleep(2)
OUT.close()
print("done")
