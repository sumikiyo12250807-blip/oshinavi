# -*- coding: utf-8 -*-
import sys, re, json, urllib.parse, urllib.request, io, os
OUT = r"C:\Users\user\oshinavi\tmp"
BS = chr(92)

def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
        "Accept-Language": "ja,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")

def balanced(html, start):
    depth = 0; i = start; instr = False; esc = False
    while i < len(html):
        c = html[i]
        if instr:
            if esc: esc = False
            elif c == BS: esc = True
            elif c == '"': instr = False
        else:
            if c == '"': instr = True
            elif c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0: return html[start:i + 1]
        i += 1
    return None

def main():
    kw = sys.argv[1]; tag = sys.argv[2]
    url = "https://eplus.jp/sf/search?keyword=" + urllib.parse.quote(kw)
    html = fetch(url)
    recs = []; seen = set()
    for m in re.finditer(r'"koen_detail_url_pc"', html):
        j = m.start(); depth = 0
        while j >= 0:
            c = html[j]
            if c == '}': depth += 1
            elif c == '{':
                if depth == 0: break
                depth -= 1
            j -= 1
        if j < 0: continue
        blob = balanced(html, j)
        if not blob: continue
        try: o = json.loads(blob)
        except Exception: continue
        k = o.get("koen_detail_url_pc")
        if k in seen: continue
        seen.add(k); recs.append(o)
    io.open(os.path.join(OUT, "zz_%s.json" % tag), "w", encoding="utf-8").write(
        json.dumps(recs, ensure_ascii=False, indent=1))
    print("OK", tag, "htmllen", len(html), "recs", len(recs))

main()
