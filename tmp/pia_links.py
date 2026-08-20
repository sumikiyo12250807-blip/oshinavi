# -*- coding: utf-8 -*-
import re, time, urllib.request

OUT = r"C:\Users\user\oshinavi\tmp\pia_links_out.txt"
URLS = [
    ("4167", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669718"),
    ("4172", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670225"),
    ("4175", "https://t.pia.jp/pia/event/event.do?eventCd=2626509"),
    ("4422", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669302"),
    ("4423", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670473"),
    ("4424", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670245"),
    ("4425", "https://t.pia.jp/pia/event/event.do?eventCd=2631967"),
]
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"}

with open(OUT, "w", encoding="utf-8") as f:
    for eid, url in URLS:
        f.write("\n######## id=%s\n" % eid)
        try:
            req = urllib.request.Request(url, headers=HDR)
            with urllib.request.urlopen(req, timeout=45) as r:
                html = r.read().decode("utf-8", "replace")
        except Exception as e:
            f.write("ERROR %s\n" % e)
            continue
        links = set()
        for m in re.finditer(r'href="([^"]+)"', html):
            h = m.group(1)
            if any(k in h for k in ["w.pia.jp", "lot", "ticketInformation", "rlsCd", "eventCd", "artists.do", "reserve"]):
                links.add(h)
        for h in sorted(links):
            f.write("  %s\n" % h)
        time.sleep(4)
print("ok")
