# -*- coding: utf-8 -*-
"""構築した74件のうち、同名の既存エントリがあるものを突合する。
ツアーの別公演なら既存へ ticket を足す（feedback_tour_consolidate）。
別興行なら新エントリにする。判断材料として、既存側の会場・公演日・ぴあURLを並べる。
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


built = json.load(open("tmp/built_0906.json", encoding="utf-8"))
h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

bykey = {}
for e in EVENTS:
    bykey.setdefault(norm(e.get("artist") or e.get("name")), []).append(e)


def pia(e):
    return ((e.get("links") or {}).get("pia") or "")


hits, fresh = [], []
for b in built:
    k = norm(b.get("artist"))
    ex = bykey.get(k) or []
    if ex:
        hits.append((b, ex))
    else:
        fresh.append(b)

print("=== 同名の既存エントリがある %d件（統合を検討） ===" % len(hits))
for b, ex in hits:
    print("")
    print("新 id=%s %s" % (b["id"], b.get("artist")))
    print("    公演%s  %s" % (b.get("date"), (b.get("venue") or "")[:70]))
    print("    %s" % pia(b))
    for t in (b.get("tickets") or []):
        print("      枠 %s （〜%s）" % (t.get("type"), t.get("date")))
    for e in ex:
        print("  既存 id=%s  公演%s  %s" % (e["id"], e.get("date"), (e.get("venue") or "")[:60]))
        print("      %s" % pia(e))
        print("      枠数 %d" % len(e.get("tickets") or []))

print("")
print("=== 完全新規 %d件 ===" % len(fresh))
for b in fresh:
    print("  id=%s %s / 公演%s / %s" % (b["id"], b.get("artist"), b.get("date"),
                                       (b.get("venue") or "")[:50]))
