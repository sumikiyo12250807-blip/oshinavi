# -*- coding: utf-8 -*-
"""e+新着49件の実ページから「公演名」と「出演者ブロック」を機械で取り、
artist を直すための材料を tmp/eplus_artist_src_0906.txt に書き出す。
"""
import re, sys, json, time, html as H, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

src = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", src, re.S)
EVENTS = json.loads(m.group(2))

def is_eplus(e):
    return "eplus.jp" in json.dumps(e, ensure_ascii=False)

pool = sorted([e for e in EVENTS if e.get("genre") == "new" and is_eplus(e)],
              key=lambda e: e["id"])

def strip_tags(s):
    s = re.sub(r'<br\s*/?>', ' / ', s)
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', H.unescape(s)).strip()

out = open("tmp/eplus_artist_src_0906.txt", "w", encoding="utf-8")
for e in pool:
    url = (e.get("links") or {}).get("eplus")
    ldname, cast = "", ""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        page = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
        for ld in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', page, re.S):
            try:
                d = json.loads(ld)
            except Exception:
                continue
            if isinstance(d, dict) and d.get("name"):
                ldname = d["name"]
                break
        mm = re.search(r'出演[^<]{0,10}</[^>]+>\s*<[^>]+>(.{0,900}?)</(?:dd|div|td|p)>', page, re.S)
        if mm:
            cast = strip_tags(mm.group(1))
    except Exception as ex:
        cast = "FETCH_ERROR:%s" % ex
    out.write("id=%d\n" % e["id"])
    out.write("  artist_now : %s\n" % (e.get("artist") or ""))
    out.write("  name       : %s\n" % (e.get("name") or ""))
    out.write("  ld_name    : %s\n" % ldname)
    out.write("  cast       : %s\n" % cast[:600])
    out.write("  genre_draft: %s\n" % (e.get("_genre") or "-"))
    out.write("  url        : %s\n\n" % url)
    out.flush()
    time.sleep(2)
out.close()
print("done: %d件" % len(pool))
