# -*- coding: utf-8 -*-
import re, ssl, time, urllib.request

OUT = r"C:\Users\user\oshinavi\tmp\misc_fetch_out.txt"
URLS = [
    ("4167 wpia tour26", "https://w.pia.jp/t/kenyokoyama-tour26/"),
    ("4425 subaruhall event list", "http://subaruhall.org/event/"),
    ("4422 wpia guess", "https://w.pia.jp/t/yeti-tour26/"),
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
        html = None
        for enc in ("utf-8", "cp932", "euc-jp"):
            try:
                cand = raw.decode(enc)
                if enc == "utf-8" or "\ufffd" not in cand:
                    html = cand
                    break
            except Exception:
                continue
        if html is None:
            html = raw.decode("utf-8", "replace")
        # detect charset meta
        m = re.search(rb'charset=["\']?([A-Za-z0-9_-]+)', raw[:2000])
        if m:
            enc = m.group(1).decode("ascii", "ignore").lower()
            try:
                html = raw.decode(enc)
            except Exception:
                pass
        f.write("---- TEXT ----\n")
        f.write(strip(html)[:8000] + "\n")
        time.sleep(3)
print("ok")
