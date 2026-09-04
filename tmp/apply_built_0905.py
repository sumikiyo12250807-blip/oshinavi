# -*- coding: utf-8 -*-
"""build_pia_entries.py の出力で、既存エントリの tickets（と公演日まわり）を差し替える。
新着プールの子を取り直した時に使う。ジャンルの下書きと id は据え置き。

使い方: python tmp/apply_built_0905.py tmp/built_6518_0905.json
🚨 読み書きは newline 未指定（テキストモード往復）＝CRLF を壊さない。
"""
import json, re, sys, datetime

PATH = "index.html"
built = {e["id"]: e for e in json.load(open(sys.argv[1], encoding="utf-8"))}

h = open(PATH, encoding="utf-8").read()
m = re.search(r"(const EVENTS = )(\[.*?\])(;\n)", h, re.S)
events = json.loads(m.group(2))
by = {e["id"]: e for e in events}

changed = []
for i, b in built.items():
    e = by.get(i)
    if not e:
        print("SKIP id=%s（現物に無い）" % i)
        continue
    before = len(e.get("tickets", []))
    # 🚨 既存の非ぴあ枠は残す（build はぴあ枠しか作らない）
    keep = [t for t in (e.get("tickets") or [])
            if (t.get("url") or "") and "pia.jp" not in (t.get("url") or "")]
    e["tickets"] = list(b["tickets"]) + keep
    for f in ("date", "dateLabel", "venue", "prefecture"):
        if b.get(f):
            e[f] = b[f]
    e["verifiedAt"] = datetime.date.today().isoformat()
    changed.append((i, before, len(e["tickets"]), len(keep)))

bak = "index.html.bak_%s_applybuilt" % datetime.date.today().strftime("%m%d")
open(bak, "w", encoding="utf-8").write(h)
new_arr = json.dumps(events, ensure_ascii=False, indent=2)
open(PATH, "w", encoding="utf-8").write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
for i, b0, b1, k in changed:
    print("id=%s 枠 %d -> %d（非ぴあ据置 %d）" % (i, b0, b1, k))
print("backup=%s" % bak)
