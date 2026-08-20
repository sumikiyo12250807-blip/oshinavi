# -*- coding: utf-8 -*-
"""新着プール53件をジャンルへ振り分ける（ユーザー明示OK済み 2026-08-01）。

ルール（project_vendor_genre_autoassign）:
  - _genre をそのまま genre に移す。自分で再分類しない。
  - 適用後は _genre / _extraGenres / _piaSub を削除。
  - NEW_ORDER は空にする（配列だけ残ると空タブになる）。
ユーザー確定の上書き:
  3521 jazz / 3523 dento / 3525 dento（7/31確定）
  3550 engeki + extraGenres:["kids"]（7/31確定）
  3570 jpop（8/1確定・カフェコラボでも主役がJ-POPならjpop）
  3564 / 3565 classic（8/1確定・_genre と同じ）
index.html はバイナリで読み書き。挿入行もCRLF。
"""
import io
import os
import re
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0801_assign"

OVERRIDE = {3521: "jazz", 3523: "dento", 3525: "dento", 3550: "engeki",
            3570: "jpop", 3564: "classic", 3565: "classic"}
EXTRA_OVERRIDE = {3550: ["kids"]}

raw = open(P, "rb").read()
s = raw.decode("utf-8")
crlf0, lf0 = raw.count(b"\r\n"), raw.count(b"\n")
print("適用前: CRLF %d / 単独LF %d / genre:new %d件" % (
    crlf0, lf0 - crlf0, s.count('"genre": "new",')))

if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)
    print("バックアップ: %s" % BAK)

BLOCK = re.compile(
    r'    "genre": "new",\r\n'
    r'    "_genre": "([^"]*)",\r\n'
    r'    "_extraGenres": (\[\]|\[\r\n(?:      "[^"]*",?\r\n)+    \]),\r\n'
    r'    "_piaSub": "([^"]*)",\r\n'
)

done, counts = [], {}
pos = 0
while True:
    m = re.compile(r'    "id": (\d+),\r\n').search(s, pos)
    if not m:
        break
    eid = int(m.group(1))
    pos = m.end()
    bm = BLOCK.search(s, m.end(), m.end() + 4000)
    if not bm:
        continue  # 新着でないエントリ
    draft_g, extra_raw, _sub = bm.group(1), bm.group(2), bm.group(3)
    g = OVERRIDE.get(eid, draft_g)
    if eid in EXTRA_OVERRIDE:
        extras = EXTRA_OVERRIDE[eid]
    else:
        extras = re.findall(r'"([^"]*)"', extra_raw)

    new_block = '    "genre": "%s",\r\n' % g
    if extras:
        new_block += '    "extraGenres": [\r\n'
        new_block += "".join(
            '      "%s"%s\r\n' % (x, "," if i < len(extras) - 1 else "")
            for i, x in enumerate(extras))
        new_block += '    ],\r\n'

    s = s[:bm.start()] + new_block + s[bm.end():]
    pos = bm.start() + len(new_block)
    done.append((eid, g, extras))
    counts[g] = counts.get(g, 0) + 1

# NEW_ORDER を空に
no = re.search(r'(  const NEW_ORDER = )\[[^\]]*\](;)', s)
if not no:
    print("🚨 NEW_ORDER が見つからない。中止。")
    sys.exit(1)
s = s[:no.start()] + no.group(1) + "[]" + no.group(2) + s[no.end():]

out = s.encode("utf-8")
crlf1, lf1 = out.count(b"\r\n"), out.count(b"\n")
assert lf1 - crlf1 == 0, "🚨 単独LFが混入した"
assert s.count('"genre": "new",') == 0, "🚨 genre:new が残っている"
open(P, "wb").write(out)

print("\n振り分け %d件:" % len(done))
for g in sorted(counts, key=lambda x: -counts[x]):
    print("  %-9s %d件" % (g, counts[g]))
ex = [(i, g, e) for i, g, e in done if e]
print("\nextraGenres 付き %d件:" % len(ex))
for i, g, e in ex:
    print("  id=%s %s +%s" % (i, g, ",".join(e)))
print("\n適用後: CRLF %d / 単独LF %d / genre:new 0件 / NEW_ORDER 空" % (crlf1, lf1 - crlf1))
