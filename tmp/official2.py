# -*- coding: utf-8 -*-
import re, ssl, time, urllib.request

OUT = r"C:\Users\user\oshinavi\tmp\official2_out.txt"
URLS = [
    ("4422 yeti BASE tour", "https://yuki0t0ko.thebase.in/p/00005"),
    ("4167 smash", "https://smash-jpn.com/live/?id=4649"),
    ("4167 kenyokoyama live", "https://kenyokoyama.com/live/"),
    ("4172 Bocchi eplus word", "https://eplus.jp/sf/word/0000162332"),
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
        m = re.search(rb'charset=["\']?([A-Za-z0-9_-]+)', raw[:3000])
        enc = m.group(1).decode("ascii", "ignore") if m else "utf-8"
        try:
            html = raw.decode(enc)
        except Exception:
            html = raw.decode("utf-8", "replace")
        f.write("---- ticket hrefs ----\n")
        seen = set()
        for mm in re.finditer(r'href="([^"]+)"', html):
            h = mm.group(1)
            if any(k in h.lower() for k in ["w.pia", "t.pia", "eplus", "l-tike", "tiget", "livepocket", "zaiko", "peatix", "ticket"]):
                if h not in seen:
                    seen.add(h)
                    f.write("  %s\n" % h)
        f.write("---- 一般発売 context ----\n")
        t = strip(html)
        for mm in re.finditer(r"一般発売|一般販売|発売日|チケット発売", t):
            f.write("  ...%s...\n" % t[max(0, mm.start() - 400):mm.start() + 400].replace("\n", " / "))
        f.write("  textlen=%d\n" % len(t))
        time.sleep(3)
print("ok")
