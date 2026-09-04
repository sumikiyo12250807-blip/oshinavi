# -*- coding: utf-8 -*-
"""ヒールの「買える枠ゼロ」候補75件を、昼に処理しやすいよう性質で分類する。
🚨 売り切れ（soldout=True）は削除しない＝「予定枚数終了」で表示し続ける（feedback_soldout_keep_visible）。"""
import json, re, io

IDS = [int(x) for x in io.open("tmp/heal_delcand_ids_0905.txt", encoding="utf-8").read().strip().split(",")]
OUT = "tmp/delcand_class_0905.txt"

html = open("index.html", encoding="utf-8").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", html, re.S).group(1))
by = {e["id"]: e for e in events}

groups = {"全枠が売り切れ": [], "一部売り切れ": [], "売り切れ無し（期限切れのみ）": [], "非ぴあ枠あり": []}
for i in IDS:
    e = by.get(i)
    if not e:
        continue
    ts = e.get("tickets") or []
    nonpia = [t for t in ts if (t.get("url") or "") and "pia.jp" not in (t.get("url") or "")]
    sold = [t for t in ts if t.get("soldout")]
    if nonpia:
        groups["非ぴあ枠あり"].append(e)
    elif ts and len(sold) == len(ts):
        groups["全枠が売り切れ"].append(e)
    elif sold:
        groups["一部売り切れ"].append(e)
    else:
        groups["売り切れ無し（期限切れのみ）"].append(e)

buf = []
for k, g in groups.items():
    buf.append("=== %s … %d件 ===" % (k, len(g)))
    for e in g:
        buf.append("  id=%-5s %s | 公演%s | 枠%d"
                   % (e["id"], e.get("name", "")[:44], e.get("date"), len(e.get("tickets", []))))
    buf.append("")
io.open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print(" / ".join("%s=%d" % (k.encode("ascii", "backslashreplace").decode(), len(v)) for k, v in groups.items()))
print("counts: %s" % json.dumps({k: len(v) for k, v in groups.items()}, ensure_ascii=False).encode("ascii", "backslashreplace").decode())
