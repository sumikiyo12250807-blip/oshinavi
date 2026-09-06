# -*- coding: utf-8 -*-
"""統合待ち34件を型で分ける（実ページを叩かずに、登録済みデータだけで分類する）。

A型＝同じ公演日・同じ会場の既存がある＝「ぴあのeventCdが別なだけ」→ 既存に枠を足して新側を欠番に
B型＝同じアーティストで公演日/会場が違う＝同じツアーの別公演の可能性 → 1エントリに畳む（千秋楽の取り直しが要る）
C型＝既存が複数あって行き先を決められない → 保留
"""
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding="utf-8")


def norm(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[\s　・･/／＆&'’\"”「」『』()（）\[\]【】-]", "", s)
    return s.lower()


h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e["id"]: e for e in EVENTS}

NEW = [e for e in EVENTS if 7025 <= e["id"] <= 7098]

bykey = {}
for e in EVENTS:
    if e["id"] >= 7025:
        continue
    bykey.setdefault(norm(e.get("artist") or e.get("name")), []).append(e)

A, B, C = [], [], []
for b in NEW:
    ex = bykey.get(norm(b.get("artist"))) or []
    if not ex:
        continue
    same = [e for e in ex if e.get("date") == b.get("date")
            and norm(e.get("venue")) == norm(b.get("venue"))]
    if len(same) == 1:
        A.append((b, same[0]))
    elif len(ex) == 1:
        B.append((b, ex[0]))
    else:
        C.append((b, ex))


def pia(e):
    return ((e.get("links") or {}).get("pia") or "")


print("=== A型：同じ公演日・同じ会場の既存がある（ぴあのeventCdが別なだけ）%d件 ===" % len(A))
for b, e in A:
    print("  新%-5d → 既存%-5d  %s" % (b["id"], e["id"], b.get("artist")))
    print("        公演%s %s" % (b.get("date"), (b.get("venue") or "")[:50]))
    print("        新の枠 %d / 既存の枠 %d" % (len(b.get("tickets") or []), len(e.get("tickets") or [])))
    print("        新 %s" % pia(b))
    print("        既 %s" % pia(e))

print("")
print("=== B型：同じアーティストで既存が1件だけ（同じツアーの別公演か要確認）%d件 ===" % len(B))
for b, e in B:
    print("  新%-5d ↔ 既存%-5d  %s" % (b["id"], e["id"], b.get("artist")))
    print("        新   公演%s %s" % (b.get("date"), (b.get("venue") or "")[:50]))
    print("        既存 公演%s %s" % (e.get("date"), (e.get("venue") or "")[:50]))

print("")
print("=== C型：既存が複数あって行き先を決められない %d件 ===" % len(C))
for b, ex in C:
    print("  新%-5d  %s  公演%s %s" % (b["id"], b.get("artist"), b.get("date"),
                                     (b.get("venue") or "")[:40]))
    for e in ex:
        print("        既存%-5d 公演%s %s" % (e["id"], e.get("date"), (e.get("venue") or "")[:40]))

print("")
print("A=%d B=%d C=%d / 合計 %d" % (len(A), len(B), len(C), len(A) + len(B) + len(C)))
json.dump({"A": [[b["id"], e["id"]] for b, e in A],
           "B": [[b["id"], e["id"]] for b, e in B],
           "C": [[b["id"], [e["id"] for e in ex]] for b, ex in C]},
          open("tmp/merge_plan_0906.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
