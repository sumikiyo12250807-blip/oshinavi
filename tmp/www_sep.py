# -*- coding: utf-8 -*-
import re, ssl, urllib.request

OUT = r"C:\Users\user\oshinavi\tmp\www_sep_out.txt"
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
TAG = re.compile(r"<[^>]+>")


def strip(h):
    h = re.sub(r"(?is)<script.*?</script>", " ", h)
    h = re.sub(r"(?is)<style.*?</style>", " ", h)
    return "\n".join([x.strip() for x in TAG.sub("\n", h).split("\n") if x.strip()])


req = urllib.request.Request("https://www-shibuya.jp/schedule/202609.php", headers=HDR)
with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
    html = r.read().decode("utf-8", "replace")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("len=%d bocchi=%s\n" % (len(html), "Bocchi" in html))
    t = strip(html)
    if "Bocchi" in t:
        for m in re.finditer("Bocchi", t):
            f.write("HIT ...%s...\n" % t[max(0, m.start() - 500):m.start() + 500].replace("\n", " / "))
        # find the detail page link near 26
        idx = html.find("Bocchi")
        seg = html[max(0, idx - 3000):idx + 1500]
        f.write("---- hrefs ----\n")
        for m in re.finditer(r'href="([^"]+)"', seg):
            f.write("  %s\n" % m.group(1))
    else:
        # list 26 Sat block
        m = re.search(r"26\nSat", t)
        f.write("no Bocchi. 26Sat idx=%s\n" % (m.start() if m else None))
        if m:
            f.write(t[m.start():m.start() + 1500])
print("ok")
