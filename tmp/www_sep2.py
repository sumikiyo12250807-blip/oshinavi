# -*- coding: utf-8 -*-
import re, ssl, urllib.request

OUT = r"C:\Users\user\oshinavi\tmp\www_sep2_out.txt"
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

t = strip(html)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("余命譚 in html: %s\n" % ("余命譚" in html))
    f.write("full text length %d\n" % len(t))
    f.write(t)
print("ok")
