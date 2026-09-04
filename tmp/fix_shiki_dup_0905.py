# -*- coding: utf-8 -*-
"""id72「劇団四季『アナと雪の女王』東京」に混入した、id6800「リトルマーメイド／舞浜」の
千葉 R9年4〜9月の6枠を外す。

裏取り＝ぴあ実ページ eventCd=2631939 は「劇団四季『リトルマーメイド』舞浜アンフィシアター
2027年4月1日〜4月25日（千葉県）」＝アナ雪ではない。6枠とも券種名・eventCd が id6800 と完全一致。

🚨 読み書きは newline 未指定（テキストモード往復）。CRLF を壊さない。
"""
import json, re, io, datetime

PATH = "index.html"
DUP_CDS = {"2631939", "2631941", "2631945", "2631950", "2631952", "2631953"}

h = open(PATH, encoding="utf-8").read()
m = re.search(r"(const EVENTS = )(\[.*?\])(;\n)", h, re.S)
events = json.loads(m.group(2))
by = {e["id"]: e for e in events}

e72, e6800 = by[72], by[6800]

def cds(ev):
    out = set()
    for t in ev.get("tickets", []):
        mm = re.search(r"event(?:Bundle)?Cd=(\w+)", t.get("url") or "")
        if mm:
            out.add(mm.group(1))
    return out

# 前提の確認＝6枠とも id6800 側に存在すること（消しても情報が失われない）
assert DUP_CDS <= cds(e6800), "6800側に無いeventCdがある: %s" % (DUP_CDS - cds(e6800))

before = len(e72["tickets"])
removed = []
kept = []
for t in e72["tickets"]:
    mm = re.search(r"event(?:Bundle)?Cd=(\w+)", t.get("url") or "")
    if mm and mm.group(1) in DUP_CDS:
        removed.append(t.get("type"))
    else:
        kept.append(t)
e72["tickets"] = kept

# 会場欄からも舞浜アンフィシアターを外す（千葉の枠が無くなるので残す理由がない）
v = e72.get("venue") or ""
mv = re.match(r"全国ツアー（(.*)）$", v)
if mv:
    vs = [x for x in mv.group(1).split("／") if "舞浜アンフィシアター" not in x]
    e72["venue"] = vs[0] if len(vs) == 1 else "全国ツアー（" + "／".join(vs) + "）"

bak = "index.html.bak_%s_shiki" % datetime.date.today().strftime("%m%d")
open(bak, "w", encoding="utf-8").write(h)
new_arr = json.dumps(events, ensure_ascii=False, indent=2)
open(PATH, "w", encoding="utf-8").write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])

io.open("tmp/fix_shiki_dup_0905.txt", "w", encoding="utf-8").write(
    "id72 の枠 %d → %d\n外した枠:\n" % (before, len(kept)) + "\n".join("  - " + r for r in removed)
    + "\n新しい venue: %s\n" % e72.get("venue"))
print("REMOVED=%d KEPT=%d backup=%s" % (len(removed), len(kept), bak))
