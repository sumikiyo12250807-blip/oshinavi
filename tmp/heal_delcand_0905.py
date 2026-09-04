# -*- coding: utf-8 -*-
"""ヒールが「買える枠ゼロ」と判定した削除候補（tmp/heal_delcand_ids_0905.txt）の中身を書き出す。
🚨 これは削除の実行リストではない。DELETE_GATE.md の「疑う6つ」を潰してから判断する。"""
import json, re, io

IDS = [int(x) for x in io.open("tmp/heal_delcand_ids_0905.txt", encoding="utf-8").read().strip().split(",")]
OUT = "tmp/heal_delcand_0905.txt"

html = open("index.html", encoding="utf-8").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", html, re.S).group(1))
by = {e["id"]: e for e in events}

buf = ["ヒールが出した「買える枠ゼロ」候補 %d件（今朝の削除10件は既に消えているので現物に無い分は除く）" % len(IDS), ""]
found = 0
for i in IDS:
    e = by.get(i)
    if not e:
        continue
    found += 1
    links = e.get("links") or {}
    buf.append("id=%-5s %s | %s(%s) | 公演%s | genre=%s | 枠%d"
               % (i, e.get("name", ""), e.get("venue", "")[:34], e.get("prefecture", ""),
                  e.get("date"), e.get("genre"), len(e.get("tickets", []))))
    for t in e.get("tickets", []):
        buf.append("    %s | startDate=%s date=%s soldout=%s"
                   % (t.get("type"), t.get("startDate"), t.get("date"), t.get("soldout")))
    for k in ("pia", "eplus", "rakuten", "lawson"):
        if links.get(k):
            buf.append("    %s: %s" % (k, links[k]))
    buf.append("")

io.open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("CANDIDATES=%d / 現物に残っている=%d -> %s" % (len(IDS), found, OUT))
