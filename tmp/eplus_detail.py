# -*- coding: utf-8 -*-
import re, time, urllib.request

OUT = r"C:\Users\user\oshinavi\tmp\eplus_detail_out.txt"
URLS = [
    ("4175-nambaHatch", "https://eplus.jp/sf/detail/0241760001-P0030040P021001"),
    ("4172-Bocchi", "https://eplus.jp/sf/detail/4503010001-P0030001P021001"),
]
HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Accept-Language": "ja,en;q=0.8",
}
TAG = re.compile(r"<[^>]+>")


def strip(h):
    h = re.sub(r"(?is)<script.*?</script>", " ", h)
    h = re.sub(r"(?is)<style.*?</style>", " ", h)
    h = TAG.sub("\n", h)
    h = h.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return "\n".join([x.strip() for x in h.split("\n") if x.strip()])


with open(OUT, "w", encoding="utf-8") as f:
    for name, url in URLS:
        f.write("\n############ %s\n%s\n" % (name, url))
        try:
            req = urllib.request.Request(url, headers=HDR)
            with urllib.request.urlopen(req, timeout=45) as r:
                f.write("HTTP %s final=%s\n" % (r.getcode(), r.geturl()))
                html = r.read().decode("utf-8", "replace")
        except Exception as e:
            f.write("ERROR %s\n" % e)
            continue
        for kw in ["受付中", "受付終了", "受付前", "予定枚数終了", "完売", "販売終了",
                   "一般発売", "先行", "抽選", "残席", "申込", "購入"]:
            if kw in html:
                f.write("  kw %s = %d\n" % (kw, html.count(kw)))
        f.write("---- TEXT ----\n")
        f.write(strip(html)[:12000])
        f.write("\n")
        time.sleep(3)
print("ok")
