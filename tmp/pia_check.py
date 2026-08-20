# -*- coding: utf-8 -*-
import re, time, urllib.request

OUT = r"C:\Users\user\oshinavi\tmp\pia_check_out.txt"

URLS = [
    ("4167", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669718"),
    ("4172", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670225"),
    ("4175", "https://t.pia.jp/pia/event/event.do?eventCd=2626509"),
    ("4422", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669302"),
    ("4423", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670473"),
    ("4424", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670245"),
    ("4425", "https://t.pia.jp/pia/event/event.do?eventCd=2631967"),
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
    lines = [x.strip() for x in h.split("\n")]
    return "\n".join([x for x in lines if x])


def main():
    with open(OUT, "w", encoding="utf-8") as f:
        for eid, url in URLS:
            f.write("\n############ id=%s\n%s\n" % (eid, url))
            try:
                req = urllib.request.Request(url, headers=HDR)
                with urllib.request.urlopen(req, timeout=45) as r:
                    code = r.getcode()
                    final = r.geturl()
                    html = r.read().decode("utf-8", "replace")
            except Exception as e:
                f.write("ERROR %s\n" % e)
                time.sleep(3)
                continue
            f.write("HTTP %s final=%s len=%d\n" % (code, final, len(html)))
            # status classes
            for cls in ["is-active", "is-before", "is-end", "is-soldout"]:
                f.write("  class %s = %d\n" % (cls, html.count(cls)))
            for kw in ["予定枚数終了", "受付終了", "販売終了", "受付中", "発売前",
                       "本サイト取扱", "取扱なし", "一般発売", "先行", "抽選"]:
                if kw in html:
                    f.write("  kw %s = %d\n" % (kw, html.count(kw)))
            txt = strip(html)
            f.write("---- TEXT ----\n")
            f.write(txt[:9000])
            f.write("\n")
            f.flush()
            time.sleep(4)
    print("done")


main()
