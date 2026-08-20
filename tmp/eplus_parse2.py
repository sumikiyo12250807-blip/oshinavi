# -*- coding: utf-8 -*-
"""Parse e+ search HTML properly: find embedded JSON objects that contain
koen_detail_url_pc and decode each object by brace matching."""
import json, re, sys, time, urllib.parse, urllib.request

OUT = r"C:\Users\user\oshinavi\tmp\eplus_parse2_out.txt"

KEYWORDS = [
    ("4167", "Ken Yokoyama"),
    ("4172", "Bocchi"),
    ("4175", "THE PREDATORS"),
    ("4422", "yeti let you notice"),
    ("4424", "シャッポ"),
]

HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Accept-Language": "ja,en;q=0.8",
}


def fetch(url):
    req = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")


def objects_containing(html, key):
    """Yield decoded dicts for every JSON object literal in html that has `key`."""
    out = []
    dec = json.JSONDecoder()
    for m in re.finditer(r'"%s"' % re.escape(key), html):
        # walk backwards to find the '{' that opens the object containing this key
        i = m.start()
        depth = 0
        j = i
        while j >= 0:
            c = html[j]
            if c == '}':
                depth += 1
            elif c == '{':
                if depth == 0:
                    break
                depth -= 1
            j -= 1
        if j < 0:
            continue
        try:
            obj, _ = dec.raw_decode(html[j:])
        except Exception:
            continue
        if isinstance(obj, dict):
            out.append(obj)
    return out


def main():
    with open(OUT, "w", encoding="utf-8") as f:
        for eid, kw in KEYWORDS:
            url = "https://eplus.jp/sf/search?keyword=" + urllib.parse.quote(kw)
            f.write("\n########## id=%s kw=%s\n%s\n" % (eid, kw, url))
            try:
                html = fetch(url)
            except Exception as e:
                f.write("ERROR %s\n" % e)
                continue
            objs = objects_containing(html, "koen_detail_url_pc")
            seen = set()
            f.write("objects=%d\n" % len(objs))
            for o in objs:
                key = json.dumps(o, ensure_ascii=False, sort_keys=True)
                if key in seen:
                    continue
                seen.add(key)
                f.write("---\n")
                f.write(json.dumps(o, ensure_ascii=False, indent=1)[:3000])
                f.write("\n")
            f.flush()
            time.sleep(2)
    print("done")


main()
