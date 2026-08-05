# -*- coding: utf-8 -*-
"""怪談候補A/Bを、既存エントリと【名前でも】突き合わせる。

eventCd照合だけだと、同じ公演をぴあが別コード(bundle と eventCd)で持っている時に
すり抜けて二重登録になる（[[feedback_harvest_dedup_check]]）。
NFKC正規化＋記号/空白除去の部分一致で「怪しい組み合わせ」を全部出す。
"""
import io
import json
import os
import re
import sys
import unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"C:\Users\user\oshinavi"


def key(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"[\s　「」『』【】≪≫＜＞<>()（）\[\]~〜～\-－ー・,、.。!！?？'\"’”]", "", s)
    return s.lower()


h = io.open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
events = json.loads(re.search(r"const EVENTS\s*=\s*(\[.*?\]);", h, re.S).group(1))
ex = [(e["id"], e.get("artist") or "", e.get("name") or "", key((e.get("artist") or "") + (e.get("name") or ""))) for e in events]

A = json.load(io.open(os.path.join(ROOT, "tmp", "kaidan_A.json"), encoding="utf-8"))
B = json.load(io.open(os.path.join(ROOT, "tmp", "kaidan_B.json"), encoding="utf-8"))

out = []
for tag, arr in (("A", A), ("B", B)):
    for r in arr:
        k = key(r["name"])
        hits = []
        for eid, art, nm, ek in ex:
            # 短い方が長い方に含まれる／先頭12文字が一致 なら疑う
            if len(k) >= 6 and (k in ek or ek in k or (len(k) >= 12 and k[:12] in ek)):
                hits.append((eid, art[:40]))
        out.append((tag, r, hits))

print("=== 既存と名前がぶつかる候補 ===")
n = 0
for tag, r, hits in out:
    if hits:
        n += 1
        print("[%s] %s" % (tag, r["name"][:56]))
        print("     %s ／ %s" % (r["day"], r["url"]))
        for eid, art in hits:
            print("     ⚠️ 既存 id%-5d %s" % (eid, art))
print("→ ぶつかり %d件 / 候補 %d件" % (n, len(out)))
print()
print("=== ぶつからない＝新規投入してよい候補 ===")
for tag, r, hits in out:
    if not hits:
        print("[%s] %-58s %s" % (tag, r["name"][:58], r["day"]))
