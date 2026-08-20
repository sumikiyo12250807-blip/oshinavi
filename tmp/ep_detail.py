# -*- coding: utf-8 -*-
import re, sys, json, time, urllib.request, io

OUTP = sys.argv[1]
URLS = sys.argv[2:]
OUT = io.open(OUTP, "w", encoding="utf-8")
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
       "Accept-Language": "ja,en;q=0.8"}


def fetch(u):
    req = urllib.request.Request(u, headers=HDR)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def dec(s):
    try:
        return json.loads('"' + s + '"')
    except Exception:
        return s


def strip_tags(h):
    h = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?s)<[^>]+>", "\n", h)
    h = h.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    lines = [x.strip() for x in h.split("\n")]
    return "\n".join([x for x in lines if x])


for u in URLS:
    if u.startswith("/"):
        u = "https://eplus.jp" + u
    OUT.write("=" * 70 + "\n" + u + "\n")
    try:
        html = fetch(u)
    except Exception as e:
        OUT.write("FETCH ERROR " + str(e) + "\n")
        OUT.flush()
        continue
    OUT.write("len=%d\n" % len(html))
    for f in ["kogyo_name_1", "kogyo_name_2", "venue_name", "koenbi_term"]:
        for m in set(re.findall(r'"' + f + r'"\s*:\s*"([^"]*)"', html)):
            OUT.write("  %s = %s\n" % (f, dec(m)))
    OUT.write("-- uketsuke records --\n")
    for m in re.finditer(r'"uketsuke_name_pc"\s*:\s*"([^"]*)"', html):
        seg = html[m.start(): m.start() + 3000]
        d = {}
        for f in ["uketsuke_start_datetime", "uketsuke_end_datetime", "uketsuke_status", "venue_name", "koenbi_term"]:
            mm = re.search(r'"' + f + r'"\s*:\s*"([^"]*)"', seg)
            if mm:
                d[f] = mm.group(1)
        OUT.write("  * %s | %s - %s | st=%s | venue=%s | koenbi=%s\n" % (
            dec(m.group(1)), d.get("uketsuke_start_datetime", ""), d.get("uketsuke_end_datetime", ""),
            d.get("uketsuke_status", ""), dec(d.get("venue_name", "")), d.get("koenbi_term", "")))
    OUT.write("-- visible text --\n")
    OUT.write(strip_tags(html)[:6000] + "\n")
    OUT.flush()
    time.sleep(2)
OUT.close()
print("done")
