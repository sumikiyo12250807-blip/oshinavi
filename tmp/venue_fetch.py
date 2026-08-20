# -*- coding: utf-8 -*-
import re, ssl, time, urllib.request

OUT = r"C:\Users\user\oshinavi\tmp\venue_fetch_out.txt"
URLS = [
    ("WWW 2026-09", "https://www-shibuya.jp/schedule/?ym=2026-09"),
    ("haremame schedule", "http://haremame.com/schedule/"),
    ("takutaku", "https://www.takutaku.info/"),
    ("kakubarhythm live", "https://kakubarhythm.com/live/"),
]
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
       "Accept-Language": "ja,en;q=0.8"}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
TAG = re.compile(r"<[^>]+>")


def strip(h):
    h = re.sub(r"(?is)<script.*?</script>", " ", h)
    h = re.sub(r"(?is)<style.*?</style>", " ", h)
    h = TAG.sub("\n", h)
    h = h.replace("&nbsp;", " ").replace("&amp;", "&")
    return "\n".join([x.strip() for x in h.split("\n") if x.strip()])


def decode(raw):
    m = re.search(rb'charset=["\']?([A-Za-z0-9_-]+)', raw[:3000])
    if m:
        try:
            return raw.decode(m.group(1).decode("ascii", "ignore"))
        except Exception:
            pass
    return raw.decode("utf-8", "replace")


with open(OUT, "w", encoding="utf-8") as f:
    for name, url in URLS:
        f.write("\n######## %s\n%s\n" % (name, url))
        try:
            req = urllib.request.Request(url, headers=HDR)
            with urllib.request.urlopen(req, timeout=45, context=ctx) as r:
                f.write("HTTP %s final=%s\n" % (r.getcode(), r.geturl()))
                raw = r.read()
        except Exception as e:
            f.write("ERROR %s\n" % e)
            time.sleep(2)
            continue
        html = decode(raw)
        t = strip(html)
        for kw in ["Bocchi", "シャッポ", "CHAPPO", "yeti", "スミワタル"]:
            if kw in html:
                f.write("  HIT kw=%s count=%d\n" % (kw, html.count(kw)))
                for m in re.finditer(re.escape(kw), t):
                    f.write("    ...%s...\n" % t[max(0, m.start() - 300):m.start() + 300].replace("\n", " / "))
        f.write("  textlen=%d\n" % len(t))
        time.sleep(3)
print("ok")
