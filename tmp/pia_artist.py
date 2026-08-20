# -*- coding: utf-8 -*-
import re, time, urllib.request

OUT = r"C:\Users\user\oshinavi\tmp\pia_artist_out.txt"
URLS = [
    ("4167 KenYokoyama", "https://t.pia.jp/pia/artist/artists.do?artistsCd=11013470"),
    ("4172 Bocchi", "https://t.pia.jp/pia/artist/artists.do?artistsCd=O4010025"),
    ("4175 PREDATORS", "https://t.pia.jp/pia/artist/artists.do?artistsCd=55160028"),
    ("4422 yeti", "https://t.pia.jp/pia/artist/artists.do?artistsCd=M3090022"),
    ("4423 TPZ", "https://t.pia.jp/pia/artist/artists.do?artistsCd=P2200028"),
    ("4424 chapo", "https://t.pia.jp/pia/artist/artists.do?artistsCd=O3190042"),
    ("4425 sumiwataru", "https://t.pia.jp/pia/artist/artists.do?artistsCd=Q8060032"),
    ("4423 wpia", "https://w.pia.jp/t/the-performance-zero26/"),
]
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
       "Accept-Language": "ja,en;q=0.8"}
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
            with urllib.request.urlopen(req, timeout=45) as r:
                f.write("HTTP %s final=%s\n" % (r.getcode(), r.geturl()))
                html = r.read().decode("utf-8", "replace")
        except Exception as e:
            f.write("ERROR %s\n" % e)
            time.sleep(3)
            continue
        evs = sorted(set(re.findall(r'event\.do\?event(?:Bundle)?Cd=([A-Za-z0-9]+)', html)))
        f.write("  eventCds: %s\n" % ", ".join(evs))
        t = strip(html)
        m = re.search(r"チケット情報|公演一覧|販売中", t)
        s = m.start() if m else 0
        f.write("---- TEXT ----\n")
        f.write(t[s:s + 6000] + "\n")
        time.sleep(4)
print("ok")
