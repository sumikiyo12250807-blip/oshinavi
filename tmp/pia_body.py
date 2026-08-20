# -*- coding: utf-8 -*-
import re, sys, time, urllib.request, io

OUTP = sys.argv[1]
URLS = sys.argv[2:]
OUT = io.open(OUTP, "w", encoding="utf-8")
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
       "Accept-Language": "ja,en;q=0.8"}


def strip_tags(h):
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
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
    OUT.write("len=%d\n" % len(html))
    for cls in ["is-active", "is-before", "is-end", "is-soldout"]:
        OUT.write("  class %s x%d\n" % (cls, html.count(cls)))
    OUT.write(strip_tags(html)[:7000] + "\n")
    OUT.flush()
    time.sleep(3)
OUT.close()
print("done")
