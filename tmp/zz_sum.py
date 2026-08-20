# -*- coding: utf-8 -*-
"""Summarize e+ search JSON records: venue / date / each uketsuke slot with dates."""
import sys, re, json, io, os

OUT = r"C:\Users\user\oshinavi\tmp"
TODAY = "20260821"

def g(d, *ks):
    for k in ks:
        if isinstance(d, dict) and d.get(k):
            return d[k]
    return ""

def name(d):
    a = g(d, "kogyo_name_1") or ""
    b = g(d, "kogyo_name_2") or ""
    c = g(d, "kogyo_sub_name") or ""
    return " / ".join([x for x in (a, b, c) if x])

def main():
    tag = sys.argv[1]
    filt = sys.argv[2] if len(sys.argv) > 2 else ""
    src = io.open(os.path.join(OUT, "ep2_%s.txt" % tag), encoding="utf-8").read()
    blobs = [b for b in src.split("\n---\n") if b.strip().startswith("{")]
    lines = []
    for b in blobs:
        try:
            d = json.loads(b)
        except Exception:
            continue
        ven = g(d, "kanren_venue") or {}
        vname = ven.get("venue_name", "") if isinstance(ven, dict) else ""
        pref = ven.get("todofuken_name", "") if isinstance(ven, dict) else ""
        hdr = "%s | %s(%s) | %s | %s" % (name(d), vname, pref, g(d, "koenbi_hyoji_mongon", "koenbi_term"),
                                          d.get("koen_detail_url_pc", ""))
        if filt and filt not in b:
            continue
        lines.append(hdr)
        slots = d.get("kanren_uketsuke_koen_list") or []
        for s in slots:
            nm = re.sub(r"&lt;|&gt;", lambda m: "<" if m.group(0) == "&lt;" else ">",
                        g(s, "uketsuke_name_pc", "uketsuke_name_mobile") or "")
            st = g(s, "uketsuke_start_datetime") or ""
            en = g(s, "uketsuke_end_datetime") or ""
            stt = g(s, "uketsuke_status")
            alive = ""
            if en and en[:8] >= TODAY:
                alive = "  <<< ALIVE?"
            lines.append("    [%s] %s  start=%s end=%s%s" % (stt, nm, st, en, alive))
        lines.append("")
    out = "\n".join(lines)
    io.open(os.path.join(OUT, "sum_%s.txt" % tag), "w", encoding="utf-8").write(out)
    print("WROTE", len(lines))

main()
