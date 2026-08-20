# -*- coding: utf-8 -*-
import sys, re, json, io, os
OUT = r"C:\Users\user\oshinavi\tmp"
TODAY = "20260821"

def main():
    tag = sys.argv[1]
    recs = json.loads(io.open(os.path.join(OUT, "zz_%s.json" % tag), encoding="utf-8").read())
    L = []
    for d in recs:
        ven = d.get("kanren_venue") or {}
        nm = " / ".join([str(d.get(k)) for k in ("kogyo_name_1", "kogyo_name_2", "kogyo_sub_name") if d.get(k)])
        L.append("%s | %s(%s) | %s | %s" % (
            nm, ven.get("venue_name", ""), ven.get("todofuken_name", ""),
            d.get("koenbi_hyoji_mongon") or d.get("koenbi_term", ""),
            d.get("koen_detail_url_pc", "")))
        for s in (d.get("kanren_uketsuke_koen_list") or []):
            u = (s.get("uketsuke_name_pc") or s.get("uketsuke_name_mobile") or "")
            u = u.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
            en = s.get("uketsuke_end_datetime") or ""
            st = s.get("uketsuke_start_datetime") or ""
            flag = "  <<<ALIVE" if en and en[:8] >= TODAY else ""
            L.append("    [st=%s] %s  %s -> %s%s" % (s.get("uketsuke_status"), u, st, en, flag))
        L.append("")
    io.open(os.path.join(OUT, "zzsum_%s.txt" % tag), "w", encoding="utf-8").write("\n".join(L))
    print("WROTE zzsum_%s.txt lines=%d" % (tag, len(L)))

main()
