# -*- coding: utf-8 -*-
import re, ssl, time, urllib.request

OUT = r"C:\Users\user\oshinavi\tmp\haremame2_out.txt"
IDS = [81870, 81588, 82211, 82370, 82425, 81920, 82488]
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
TAG = re.compile(r"<[^>]+>")


def strip(h):
    h = re.sub(r"(?is)<script.*?</script>", " ", h)
    h = re.sub(r"(?is)<style.*?</style>", " ", h)
    h = TAG.sub("\n", h)
    h = h.replace("&nbsp;", " ").replace("&amp;", "&").replace("&#8220;", '"').replace("&#8221;", '"')
    return "\n".join([x.strip() for x in h.split("\n") if x.strip()])


with open(OUT, "w", encoding="utf-8") as f:
    for i in IDS:
        url = "http://haremame.com/schedule/%d/" % i
        try:
            req = urllib.request.Request(url, headers=HDR)
            with urllib.request.urlopen(req, timeout=45, context=ctx) as r:
                raw = r.read()
        except Exception as e:
            f.write("\n#### %s ERROR %s\n" % (url, e))
            continue
        m = re.search(rb'charset=["\']?([A-Za-z0-9_-]+)', raw[:3000])
        enc = m.group(1).decode("ascii", "ignore") if m else "utf-8"
        try:
            html = raw.decode(enc)
        except Exception:
            html = raw.decode("utf-8", "replace")
        if "シャッポ" not in html:
            f.write("\n#### %s : no シャッポ\n" % url)
            time.sleep(1)
            continue
        f.write("\n#### %s : SHAPPO HIT\n" % url)
        t = strip(html)
        f.write(t[:4000] + "\n")
        f.write("---- hrefs ----\n")
        for mm in re.finditer(r'href="([^"]+)"', html):
            h = mm.group(1)
            if any(k in h.lower() for k in ["reserve", "tiget", "livepocket", "zaiko", "peatix", "eplus", "pia", "l-tike", "form", "ticket"]):
                f.write("  %s\n" % h)
        time.sleep(2)
print("ok")
