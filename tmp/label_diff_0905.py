# -*- coding: utf-8 -*-
"""記事の見出しラベル9件＝現物の dateLabel と 9/4に作った正しい候補を突き合わせる。
--apply で dateLabel（と prefecture/venue）だけを当てる。tickets や date は触らない。"""
import json, re, io, sys, datetime

CAND = "tmp/label_built_0904.json"
OUT = "tmp/label_diff_0905.txt"
PATH = "index.html"

cand = {c["id"]: c for c in json.load(io.open(CAND, encoding="utf-8"))}
h = io.open(PATH, encoding="utf-8", newline="").read()
m = re.search(r"(const EVENTS = )(\[.*?\])(;\r?\n)", h, re.S)
events = json.loads(m.group(2))
by = {e["id"]: e for e in events}

buf = []
changed = 0
for i, c in sorted(cand.items()):
    e = by.get(i)
    if not e:
        buf.append("id=%s ⚠️現物に無い（削除済み？）" % i)
        continue
    diffs = []
    for f in ("dateLabel", "prefecture", "venue", "date"):
        if (e.get(f) or "") != (c.get(f) or ""):
            diffs.append((f, e.get(f), c.get(f)))
    if not diffs:
        buf.append("id=%-5s %s : 差分なし" % (i, e.get("name", "")))
        continue
    changed += 1
    buf.append("id=%-5s %s" % (i, e.get("name", "")))
    for f, old, new in diffs:
        buf.append("    %s" % f)
        buf.append("       現物: %s" % old)
        buf.append("       候補: %s" % new)
    buf.append("")

io.open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("DIFF_ENTRIES=%d / %d  -> %s" % (changed, len(cand), OUT))

if "--apply" in sys.argv:
    n = 0
    for i, c in cand.items():
        e = by.get(i)
        if not e:
            continue
        # 🚨 dateLabel だけ当てる。date/tickets は触らない（9/4に直した内容を壊さない）
        if (e.get("dateLabel") or "") != (c.get("dateLabel") or ""):
            e["dateLabel"] = c["dateLabel"]
            n += 1
    bak = "index.html.bak_%s_label" % datetime.date.today().strftime("%m%d")
    io.open(bak, "w", encoding="utf-8", newline="").write(h)
    new_arr = json.dumps(events, ensure_ascii=False, indent=2)
    io.open(PATH, "w", encoding="utf-8", newline="").write(
        h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print("APPLIED dateLabel=%d backup=%s" % (n, bak))
