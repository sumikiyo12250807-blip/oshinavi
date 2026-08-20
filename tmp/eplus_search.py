# -*- coding: utf-8 -*-
import sys, re, json, urllib.parse, urllib.request, io, os

OUT = r"C:\Users\user\oshinavi\tmp"

def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
        "Accept-Language":"ja,en;q=0.8",
    })
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")

KEYS = ["koen_detail_url_pc","kogyo_name_1","kogyo_name_2","kogyo_sub_name","venue_name","koenbi_term","koen_date",
        "uketsuke_name_pc","uketsuke_start_datetime","uketsuke_end_datetime","uketsuke_status","kogyo_start_date","kogyo_end_date"]

def extract(html):
    # find each object containing koen_detail_url_pc, grab a window around it
    out=[]
    for m in re.finditer(r'"koen_detail_url_pc"\s*:\s*"([^"]*)"', html):
        s=max(0,m.start()-6000); e=min(len(html), m.end()+6000)
        win=html[s:e]
        rec={"koen_detail_url_pc":m.group(1)}
        for k in KEYS[1:]:
            vals = re.findall(r'"%s"\s*:\s*"([^"]*)"' % k, win)
            if vals:
                rec[k]=list(dict.fromkeys(vals))[:6]
        out.append(rec)
    return out

def main():
    kw = sys.argv[1]
    tag = sys.argv[2]
    url = "https://eplus.jp/sf/search?keyword=" + urllib.parse.quote(kw)
    try:
        html = fetch(url)
    except Exception as ex:
        open(os.path.join(OUT, "eplus_%s.txt"%tag),"w",encoding="utf-8").write("ERROR %s\n%s"%(url,ex)); print("ERR",tag,ex); return
    recs = extract(html)
    with io.open(os.path.join(OUT, "eplus_%s.txt"%tag),"w",encoding="utf-8") as f:
        f.write("URL: %s\nHTML len: %d\nrecords: %d\n\n" % (url, len(html), len(recs)))
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False, indent=1))
            f.write("\n---\n")
    print("OK", tag, "len", len(html), "recs", len(recs))

main()
