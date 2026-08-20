# -*- coding: utf-8 -*-
import re, sys, json, urllib.parse, urllib.request, io, os

KEYS = sys.argv[1:]
OUT = io.open(r"C:\Users\user\oshinavi\tmp\eplusA_out.txt","w",encoding="utf-8")

def fetch(u):
    req = urllib.request.Request(u, headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept-Language":"ja,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8","replace")

FIELDS = ["koen_detail_url_pc","kogyo_name_1","kogyo_name_2","venue_name","koenbi_term","koenbi",
          "uketsuke_name_pc","uketsuke_start_datetime","uketsuke_end_datetime","uketsuke_status"]

for kw in KEYS:
    url = "https://eplus.jp/sf/search?keyword=" + urllib.parse.quote(kw)
    OUT.write("="*70+"\nKEYWORD: %s\n%s\n"%(kw,url))
    try:
        html = fetch(url)
    except Exception as e:
        OUT.write("FETCH ERROR %s\n"%e); continue
    OUT.write("len=%d\n"%len(html))
    # split on koen_detail_url_pc occurrences
    idxs = [m.start() for m in re.finditer(r'"koen_detail_url_pc"', html)]
    OUT.write("hits=%d\n"%len(idxs))
    for i,st in enumerate(idxs):
        seg = html[max(0,st-2500): st+2500]
        rec = {}
        for f in FIELDS:
            m = re.search(r'"%s"\s*:\s*"([^"]*)"'%f, seg)
            if m: rec[f]=m.group(1)
        OUT.write("--- hit %d\n"%i)
        for f in FIELDS:
            if f in rec:
                OUT.write("   %s = %s
"%(f, json.loads('"'+rec[f]+'"') if rec[f] else rec[f]))
OUT.close()
print("done")
