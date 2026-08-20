# -*- coding: utf-8 -*-
"""3926 ジャパン・ビアフェスティバル横浜2026 を新ジャンル gourmet に確定する（2026-08-07）。
下書きフィールド(_genre/_extraGenres/_piaSub)も落とし、NEW_ORDER を空にする＝新着プール0件。
"""
import io
import os
import re
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0807_gourmet_assign"
raw = open(P, "rb").read()
crlf0, lf0 = raw.count(b"\r\n"), raw.count(b"\n")
print("修正前: CRLF %d / 単独LF %d" % (crlf0, lf0 - crlf0))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

t = raw.decode("utf-8")
changes, ng = [], []

i = t.find('"id": 3926,')
assert i > 0, "3926が見つからない"
nxt = t.find('"id": ', i + 10)
seg = t[i:nxt if nxt > 0 else len(t)]

old_seg = seg
seg = seg.replace('    "genre": "new",\r\n', '    "genre": "gourmet",\r\n', 1)
seg = re.sub(r'    "_genre": "[^"]*",\r\n', "", seg, count=1)
seg = re.sub(r'    "_extraGenres": \[\],\r\n', "", seg, count=1)
seg = re.sub(r'    "_piaSub": "[^"]*",\r\n', "", seg, count=1)
if seg == old_seg:
    ng.append("3926 の書き換えが1つも当たらなかった")
else:
    t = t[:i] + seg + (t[nxt:] if nxt > 0 else "")
    changes.append("3926 genre new → gourmet（下書きフィールドを削除）")

# NEW_ORDER を空に（並び順配列だけ残ると空の新着タブになる）
m = re.search(r"(const NEW_ORDER = )(\[[^\]]*\])(;)", t)
if not m:
    ng.append("NEW_ORDER が見つからない")
else:
    print("NEW_ORDER 変更前: %s" % m.group(2)[:80])
    t = t[:m.start(2)] + "[]" + t[m.end(2):]
    changes.append("NEW_ORDER を空にした（新着プール0件）")

b = t.encode("utf-8")
crlf1, lf1 = b.count(b"\r\n"), b.count(b"\n")
assert lf1 - crlf1 == lf0 - crlf0 == 0, "単独LFが混入した"
if ng:
    print("\n🚨 失敗があるので書き込まない: %s" % " / ".join(ng))
    sys.exit(1)
open(P, "wb").write(b)
print("\n適用 %d件:" % len(changes))
for c in changes:
    print("  ✅ %s" % c)
print("修正後: CRLF %d / 単独LF %d" % (crlf1, lf1 - crlf1))
