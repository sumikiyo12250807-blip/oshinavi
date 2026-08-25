# -*- coding: utf-8 -*-
import json, io
from collections import Counter
P = r"C:\Users\user\oshinavi\tmp\audit_expired_0824.json"
OUT = r"C:\Users\user\oshinavi\tmp\summary_c_out.txt"
d = json.load(io.open(P, encoding="utf-8"))
C = d["zero_future"]
L = []
L.append("C（公演日は未来だが買える枠ゼロ）: %d 件" % len(C))
last = Counter(max(r["ticket_dates"]) if r["ticket_dates"] else "枠なし" for r in C)
L.append("最終締切の分布（上位）: %s" % last.most_common(12))
L.append("")
L.append("公演日が今日(8/24)のもの＝明朝の削除候補予備軍:")
for r in sorted(C, key=lambda x: x["date"]):
    if r["date"] == "2026-08-24":
        L.append("  id=%s %s (最終締切 %s)" % (r["id"], r["name"][:40], max(r["ticket_dates"]) if r["ticket_dates"] else "なし"))
L.append("")
L.append("C の id 全部: %s" % ",".join(str(r["id"]) for r in sorted(C, key=lambda x: x["id"])))
L.append("")
L.append("うち最終締切が 2026-08-23（昨日切れたばかり）: %s" % ",".join(
    str(r["id"]) for r in sorted(C, key=lambda x: x["id"]) if r["ticket_dates"] and max(r["ticket_dates"]) == "2026-08-23"))
io.open(OUT, "w", encoding="utf-8").write("\n".join(L))
print("ok")
