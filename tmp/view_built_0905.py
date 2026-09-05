# -*- coding: utf-8 -*-
"""ビルド結果（entries.json）を人が読める形に書き出す。投入前の目視用。
使い方: python tmp/view_built_0905.py <built.json> [出力先.txt]
"""
import json, io, sys

src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else src.rsplit(".", 1)[0] + "_view.txt"
a = json.load(io.open(src, encoding="utf-8"))

buf = ["%s … %dエントリ / %d枠" % (src, len(a), sum(len(e.get("tickets") or []) for e in a)), ""]
for e in a:
    buf.append("■ id=%s  %s" % (e.get("id"), e.get("name", "")))
    buf.append("   artist=%s  genre=%s(下書き %s)  verified=%s"
               % (e.get("artist"), e.get("genre"), e.get("_genre"), e.get("verified")))
    buf.append("   venue=%s / %s" % (e.get("venue"), e.get("prefecture")))
    buf.append("   date=%s  dateLabel=%s" % (e.get("date"), e.get("dateLabel")))
    L = e.get("links") or {}
    buf.append("   links: " + " ".join("%s=%s" % (k, v) for k, v in L.items() if v and k != "amazon"))
    for t in e.get("tickets") or []:
        buf.append("   - %s" % t.get("type"))
        buf.append("     date=%s startDate=%s url=%s"
                   % (t.get("date"), t.get("startDate"), t.get("url") or "(なし＝カード共通リンクへ)"))
    buf.append("")

io.open(out, "w", encoding="utf-8").write("\n".join(buf))
print("wrote %s" % out)
