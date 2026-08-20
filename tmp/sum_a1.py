# -*- coding: utf-8 -*-
import io, re, sys
src, dst = sys.argv[1], sys.argv[2]
s = io.open(src, encoding="utf-8").read()
o = io.open(dst, "w", encoding="utf-8")
for blk in s.split("=" * 70):
    if not blk.strip():
        continue
    lines = blk.strip().split("\n")
    o.write("### " + lines[0] + "\n")
    seen = set()
    for hit in blk.split("--- hit ")[1:]:
        d = dict(re.findall(r"(\w+) = (.*)", hit))
        key = (d.get("koen_detail_url_pc"), d.get("uketsuke_name_pc"), d.get("venue_name"))
        if key in seen:
            continue
        seen.add(key)
        o.write("  | %s | %s | %s | %s | %s | %s-%s | st%s | %s\n" % (
            d.get("kogyo_name_1", "")[:45], d.get("kogyo_name_2", "")[:35],
            d.get("venue_name", ""), d.get("koenbi_term", ""),
            d.get("uketsuke_name_pc", ""), d.get("uketsuke_start_datetime", ""),
            d.get("uketsuke_end_datetime", ""), d.get("uketsuke_status", ""),
            d.get("koen_detail_url_pc", "")))
o.close()
print("ok")
