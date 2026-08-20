# -*- coding: utf-8 -*-
import re, sys, json, time, urllib.parse, urllib.request, io

KEYS = sys.argv[2:]
OUTP = sys.argv[1]
OUT = io.open(OUTP, "w", encoding="utf-8")

HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
       "Accept-Language": "ja,en;q=0.8"}

def fetch(u):
    req = urllib.request.Request(u, headers=HDR)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")

FIELDS = ["koen_detail_url_pc", "kogyo_name_1", "kogyo_name_2", "venue_name",
          "koenbi_term", "uketsuke_name_pc", "uketsuke_start_datetime",
          "uketsuke_end_datetime", "uketsuke_status"]

def dec(s):
    try:
        return json.loads('"' + s + '"')
    except Exception:
        return s

for kw in KEYS:
    url = "https://eplus.jp/sf/search?keyword=" + urllib.parse.quote(kw)
    OUT.write("=" * 70 + "\n")
    OUT.write("KEYWORD: " + kw + "\n" + url + "\n")
    try:
        html = fetch(url)
    except Exception as e:
        OUT.write("FETCH ERROR " + str(e) + "\n")
        OUT.flush()
        continue
    idxs = [m.start() for m in re.finditer(r'"koen_detail_url_pc"', html)]
    OUT.write("len=%d hits=%d\n" % (len(html), len(idxs)))
    for i, st in enumerate(idxs):
        seg = html[max(0, st - 2500): st + 2500]
        OUT.write("--- hit %d\n" % i)
        for f in FIELDS:
            m = re.search(r'"' + f + r'"\s*:\s*"([^"]*)"', seg)
            if m:
                OUT.write("   %s = %s\n" % (f, dec(m.group(1))))
    OUT.flush()
    time.sleep(2)
OUT.close()
print("done")
