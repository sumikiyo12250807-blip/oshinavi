# -*- coding: utf-8 -*-
import re, sys, time, urllib.parse, urllib.request, io, gzip

OUTP = sys.argv[1]
KEYS = sys.argv[2:]
OUT = io.open(OUTP, "w", encoding="utf-8")
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
       "Accept-Language": "ja,en;q=0.8", "Accept": "text/html,application/xhtml+xml"}


def strip_tags(h):
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?s)<[^>]+>", "\n", h)
    h = h.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return "\n".join([x.strip() for x in h.split("\n") if x.strip()])


for kw in KEYS:
    url = "https://l-tike.com/search/?keyword=" + urllib.parse.quote(kw)
    OUT.write("=" * 70 + "\n" + kw + "\n" + url + "\n")
    try:
        req = urllib.request.Request(url, headers=HDR)
        with urllib.request.urlopen(req, timeout=90) as r:
            raw = r.read()
        html = raw.decode("utf-8", "replace")
    except Exception as e:
        OUT.write("FETCH ERROR " + str(e) + "\n")
        OUT.flush()
        continue
    t = strip_tags(html)
    OUT.write("len=%d\n" % len(html))
    OUT.write(t[:5000] + "\n")
    OUT.flush()
    time.sleep(2)
OUT.close()
print("done")
