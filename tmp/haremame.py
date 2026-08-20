# -*- coding: utf-8 -*-
import re, ssl, urllib.request

OUT = r"C:\Users\user\oshinavi\tmp\haremame_out.txt"
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def get(url):
    req = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req, timeout=45, context=ctx) as r:
        raw = r.read()
        fin = r.geturl()
    m = re.search(rb'charset=["\']?([A-Za-z0-9_-]+)', raw[:3000])
    enc = m.group(1).decode("ascii", "ignore") if m else "utf-8"
    try:
        return fin, raw.decode(enc)
    except Exception:
        return fin, raw.decode("utf-8", "replace")


TAG = re.compile(r"<[^>]+>")


def strip(h):
    h = re.sub(r"(?is)<script.*?</script>", " ", h)
    h = re.sub(r"(?is)<style.*?</style>", " ", h)
    h = TAG.sub("\n", h)
    h = h.replace("&nbsp;", " ").replace("&amp;", "&").replace("&#8220;", '"').replace("&#8221;", '"')
    return "\n".join([x.strip() for x in h.split("\n") if x.strip()])


with open(OUT, "w", encoding="utf-8") as f:
    fin, html = get("http://haremame.com/schedule/")
    # find the block around シャッポ and pull hrefs
    idx = html.find("シャッポ")
    f.write("index=%d\n" % idx)
    seg = html[max(0, idx - 6000):idx + 4000]
    f.write("---- hrefs near シャッポ ----\n")
    for m in re.finditer(r'href="([^"]+)"', seg):
        f.write("  %s\n" % m.group(1))
    f.write("---- text near シャッポ ----\n")
    f.write(strip(seg)[-3000:] + "\n")
print("ok")
