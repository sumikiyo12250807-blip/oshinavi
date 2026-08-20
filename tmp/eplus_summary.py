# -*- coding: utf-8 -*-
import json, re, time, urllib.parse, urllib.request

OUT = r"C:\Users\user\oshinavi\tmp\eplus_summary_out.txt"

KEYWORDS = [
    ("4167", "Ken Yokoyama"),
    ("4172", "Bocchi"),
    ("4175", "THE PREDATORS"),
    ("4175", "山中さわお"),
    ("4422", "yeti let you notice"),
    ("4422", "イエティ"),
    ("4423", "The Performance Zero"),
    ("4424", "シャッポ"),
    ("4424", "磔磔"),
    ("4424", "晴れたら空に豆まいて"),
    ("4425", "スミワタルトリオ"),
    ("4425", "富田林"),
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
    out = []
    dec = json.JSONDecoder()
    for m in re.finditer(r'"%s"' % re.escape(key), html):
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
            f.write("\n########## id=%s kw=%s -> %s\n" % (eid, kw, url))
            try:
                html = fetch(url)
            except Exception as e:
                f.write("ERROR %s\n" % e)
                continue
            objs = objects_containing(html, "koen_detail_url_pc")
            seen = set()
            for o in objs:
                sub = o.get("kanren_kogyo_sub") or {}
                ven = o.get("kanren_venue") or {}
                name = "%s %s" % (sub.get("kogyo_name_1") or "", sub.get("kogyo_name_2") or "")
                line = "%s | %s (%s) | koenbi=%s | %s" % (
                    name.strip(), ven.get("venue_name"), ven.get("todofuken_name"),
                    o.get("koenbi_term"), o.get("koen_detail_url_pc"))
                if line in seen:
                    continue
                seen.add(line)
                f.write("* " + line + "\n")
                for u in (o.get("kanren_uketsuke_koen_list") or []):
                    f.write("    - %s | %s | %s ~ %s | status=%s | eplus_ari=%s\n" % (
                        u.get("uketsuke_name_pc"), u.get("hambai_hoho_label"),
                        u.get("uketsuke_start_datetime"), u.get("uketsuke_end_datetime"),
                        u.get("uketsuke_status"), u.get("eplus_toriatsukai_ari_flag")))
            f.flush()
            time.sleep(2)
    print("done")


main()
