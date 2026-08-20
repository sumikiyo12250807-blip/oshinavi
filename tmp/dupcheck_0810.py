# -*- coding: utf-8 -*-
"""投入前の重複チェック（[[feedback_harvest_dedup_check]]）＝eventCd と正規化アーティスト名の両方で見る。"""
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

src = open("index.html", "rb").read().decode("utf-8")
m = re.search(r"  const EVENTS = (\[.*?\]);", src, re.S)
EVENTS = json.loads(m.group(1))
new = json.load(open("tmp/entries2_0810.json", encoding="utf-8"))


def codes(e):
    s = json.dumps(e, ensure_ascii=False)
    return set(re.findall(r"event(?:Bundle)?Cd=([0-9a-zA-Z]+)", s))


def norm(s):
    return re.sub(r"[\s　・･]", "", unicodedata.normalize("NFKC", s or "")).lower()


old_codes = {}
for e in EVENTS:
    for c in codes(e):
        old_codes.setdefault(c, e["id"])
old_names = {}
for e in EVENTS:
    old_names.setdefault(norm(e.get("artist")), []).append(e["id"])

hit = 0
for e in new:
    dup = [(c, old_codes[c]) for c in codes(e) if c in old_codes]
    nm = old_names.get(norm(e.get("artist")))
    if dup or nm:
        hit += 1
        print("id=%d %s" % (e["id"], (e.get("artist") or "")[:30]))
        if dup:
            print("    ⚠️eventCd重複: %s" % dup[:4])
        if nm:
            print("    ⚠️同名の既存エントリ: %s" % nm[:6])
print("=== 新規%d件 / 引っかかり%d件 ===" % (len(new), hit))
