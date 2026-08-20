# -*- coding: utf-8 -*-
import json, re, sys, time, urllib.parse, urllib.request

OUT = r"C:\Users\user\oshinavi\tmp\eplus_probe_out.txt"

KEYWORDS = [
    ("4167", "Ken Yokoyama"),
    ("4167", "ケンヨコヤマ"),
    ("4167", "Pizza of Death"),
    ("4172", "Bocchi"),
    ("4172", "ぼっち"),
    ("4175", "THE PREDATORS"),
    ("4175", "PREDATORS"),
    ("4422", "yeti let you notice"),
    ("4422", "yeti"),
    ("4423", "The Performance Zero"),
    ("4423", "Performance Zero"),
    ("4424", "シャッポ"),
    ("4424", "chapeau"),
    ("4425", "スミワタルトリオ"),
    ("4425", "すばるホール"),
]

FIELDS = ["kogyo_name_1", "kogyo_name_2", "venue_name", "koenbi_term",
          "koen_start_datetime", "uketsuke_name_pc", "uketsuke_start_datetime",
          "uketsuke_end_datetime", "koen_detail_url_pc", "uketsuke_status"]

HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Accept-Language": "ja,en;q=0.8",
}


def fetch(url):
    req = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")


def probe(kw):
    url = "https://eplus.jp/sf/search?keyword=" + urllib.parse.quote(kw)
    try:
        html = fetch(url)
    except Exception as e:
        return url, "ERROR %s" % e, []
    # find all occurrences of koen_detail_url_pc and grab a window around each
    hits = []
    for m in re.finditer(r'"koen_detail_url_pc"\s*:\s*"([^"]+)"', html):
        start = max(0, m.start() - 4000)
        end = min(len(html), m.end() + 4000)
        window = html[start:end]
        rec = {"detail": m.group(1)}
        for f in FIELDS:
            fm = None
            # nearest occurrence of field in window
            for fm2 in re.finditer(r'"%s"\s*:\s*"([^"]*)"' % f, window):
                fm = fm2
                if fm2.start() > (m.start() - start):
                    break
            if fm:
                rec[f] = fm.group(1)
        hits.append(rec)
    # dedupe by detail url
    seen = set()
    uniq = []
    for h in hits:
        if h["detail"] in seen:
            continue
        seen.add(h["detail"])
        uniq.append(h)
    return url, "OK len=%d" % len(html), uniq


def main():
    with open(OUT, "w", encoding="utf-8") as f:
        for eid, kw in KEYWORDS:
            url, status, hits = probe(kw)
            f.write("\n=== id=%s keyword=%s\n%s\n%s hits=%d\n" % (eid, kw, url, status, len(hits)))
            for h in hits[:25]:
                f.write("  - detail=%s\n" % h.get("detail"))
                for k in ["kogyo_name_1", "kogyo_name_2", "venue_name", "koenbi_term",
                          "koen_start_datetime", "uketsuke_name_pc",
                          "uketsuke_start_datetime", "uketsuke_end_datetime"]:
                    if h.get(k):
                        f.write("      %s = %s\n" % (k, h.get(k)))
            f.flush()
            time.sleep(2)
    print("done ->", OUT)


main()
