# -*- coding: utf-8 -*-
"""新着46件（id3572-3621・欠番4）を index.html に投入し、NEW_ORDER を張り替える。
🚨 インデントは既存に合わせて「オブジェクト2sp／フィールド4sp」＝json.dumps(indent=2)+2sp。
🚨 json.dumps の出力は LF なので必ず CRLF に直す（feedback_index_html_crlf_preserve）。
欠番(3589/3608/3614/3615)は詰めない（feedback_candidate_list_stable_numbering）。"""
import io
import json
import os
import re
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0801_new46"
E = r"C:\Users\user\oshinavi\tmp\entries_0801_pm.json"

ents = json.load(open(E, encoding="utf-8"))
ids = [e["id"] for e in ents]
assert all(e.get("genre") == "new" for e in ents), "genre:new でないものが混じっている"

raw = open(P, "rb").read()
s = raw.decode("utf-8")
crlf0, lf0 = raw.count(b"\r\n"), raw.count(b"\n")
print("投入前: CRLF %d / 単独LF %d / genre:new %d件" % (crlf0, lf0 - crlf0, s.count('"genre": "new",')))

# 既存重複チェック（eventCd と id）
dup = [i for i in ids if ('"id": %d,' % i) in s]
if dup:
    print("🚨 既に存在するid: %s。中止。" % dup)
    sys.exit(1)
dupcd = []
for e in ents:
    pia = (e.get("links") or {}).get("pia") or ""
    m = re.search(r"(eventCd|eventBundleCd)=([A-Za-z0-9]+)", pia)
    if m and m.group(2) in s:
        dupcd.append((e["id"], m.group(2)))
if dupcd:
    print("🚨 既に登録済みのぴあコード: %s。中止。" % dupcd)
    sys.exit(1)

if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)
    print("バックアップ: %s" % BAK)

# --- エントリ本体を整形（フィールド4sp）---
blocks = []
for e in ents:
    body = json.dumps(e, ensure_ascii=False, indent=2)
    body = "\n".join("  " + ln for ln in body.split("\n"))
    blocks.append(body.replace("\n", "\r\n"))

TAIL = "\r\n  }\r\n];"
if s.count(TAIL) != 1:
    print("🚨 配列終端のヒット数が1でない。中止。")
    sys.exit(1)
s = s.replace(TAIL, "\r\n  },\r\n" + ",\r\n".join(blocks) + "\r\n];")

# --- NEW_ORDER を張り替え ---
no = re.search(r"(  const NEW_ORDER = )\[[^\]]*\](;)", s)
if not no:
    print("🚨 NEW_ORDER が見つからない。中止。")
    sys.exit(1)
s = s[:no.start()] + no.group(1) + "[" + ", ".join(str(i) for i in ids) + "]" + no.group(2) + s[no.end():]

out = s.encode("utf-8")
crlf1, lf1 = out.count(b"\r\n"), out.count(b"\n")
assert lf1 - crlf1 == 0, "🚨 単独LFが混入した"
open(P, "wb").write(out)

print("✅ %d件を投入 / NEW_ORDER %d件" % (len(ents), len(ids)))
print("   欠番: 3589, 3608, 3614, 3615（ぴあに買える枠が無くbuildがskip）")
print("投入後: CRLF %d / 単独LF %d" % (crlf1, lf1 - crlf1))
