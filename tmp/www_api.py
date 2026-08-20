# -*- coding: utf-8 -*-
import re, ssl, urllib.request

OUT = r"C:\Users\user\oshinavi\tmp\www_api_out.txt"
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request("https://www-shibuya.jp/schedule/", headers=HDR)
with urllib.request.urlopen(req, timeout=45, context=ctx) as r:
    html = r.read().decode("utf-8", "replace")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("---- script srcs ----\n")
    for m in re.finditer(r'<script[^>]*src="([^"]+)"', html):
        f.write("  %s\n" % m.group(1))
    f.write("---- ajax/json hints ----\n")
    for m in re.finditer(r'["\'](/[^"\']*(?:json|api|ajax|schedule)[^"\']*)["\']', html):
        f.write("  %s\n" % m.group(1))
    f.write("---- month links ----\n")
    for m in re.finditer(r'href="([^"]*schedule[^"]*)"', html):
        f.write("  %s\n" % m.group(1))
    f.write("---- data attrs ----\n")
    for m in re.finditer(r'data-[a-z-]+="[^"]{0,80}"', html):
        f.write("  %s\n" % m.group(0))
print("ok")
