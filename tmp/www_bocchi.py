# -*- coding: utf-8 -*-
import re, ssl, time, urllib.request

OUT = r"C:\Users\user\oshinavi\tmp\www_bocchi_out.txt"
URLS = [
    "https://www-shibuya.jp/schedule/",
    "https://www-shibuya.jp/schedule/?y=2026&m=09",
    "https://www-shibuya.jp/schedule/index.php?y=2026&m=9",
    "https://tiget.net/search?q=Bocchi",
    "https://t.livepocket.jp/search?keyword=Bocchi",
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
    return "\n".join([x.strip() for x in h.split("\n") if x.strip()])


with open(OUT, "w", encoding="utf-8") as f:
    for url in URLS:
        f.write("\n######## %s\n" % url)
        try:
            req = urllib.request.Request(url, headers=HDR)
            with urllib.request.urlopen(req, timeout=45, context=ctx) as r:
                f.write("HTTP %s final=%s\n" % (r.getcode(), r.geturl()))
                raw = r.read()
        except Exception as e:
            f.write("ERROR %s\n" % e)
            time.sleep(2)
            continue
        m = re.search(rb'charset=["\']?([A-Za-z0-9_-]+)', raw[:3000])
        enc = m.group(1).decode("ascii", "ignore") if m else "utf-8"
        try:
            html = raw.decode(enc)
        except Exception:
            html = raw.decode("utf-8", "replace")
        t = strip(html)
        f.write("  textlen=%d  bocchi_in_html=%s\n" % (len(t), "Bocchi" in html or "BOCCHI" in html.upper()))
        # list dates present
        dates = sorted(set(re.findall(r"20\d\d[./-]\d{1,2}[./-]\d{1,2}", t)))[:60]
        f.write("  dates: %s\n" % ", ".join(dates))
        if "Bocchi" in html:
            for mm in re.finditer("Bocchi", t):
                f.write("  HIT ...%s...\n" % t[max(0, mm.start() - 300):mm.start() + 300].replace("\n", " / "))
        f.write("  head: %s\n" % t[:600].replace("\n", " / "))
        time.sleep(3)
print("ok")
