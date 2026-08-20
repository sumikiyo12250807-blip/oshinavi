# -*- coding: utf-8 -*-
"""振り分け前に下書きジャンル(_genre/_extraGenres)を直す（2026-08-07）。

  3888 南大阪オカリナフェスタ2026  fes → classic
       会場が堺市民芸術文化ホール「小ホール」＝屋内。fesは複数組＋屋外が条件（feedback_fes_definition）。
       ぴあのサブが「音楽/音楽その他」＝名前ベースfallbackで「フェスタ」に引っかかった型。
  迷うものは主＋extraGenresで両方入れる（feedback_genre_both_when_unclear）:
  3896 伊藤蘭 クリスマスディナー&コンサート  jpop +dinnershow（ホテルの大広間＝ディナーショー）
  3897 鈴木雅之 X'mas Private Hotel Tour   jpop +dinnershow（同上）
  3913 オーケストラで聴くアニメ音楽の世界     classic +anime
  3919 MANSAI FANTASY BOX 野村萬斎 with OEK classic +dento（主役が狂言師）
  3923 光が死んだ夏展 福岡会場              art +anime（原作アニメ/漫画の展示）

index.html はバイナリで読み書きしCRLFを保つ。エントリ内の位置を特定してから置換する。
"""
import io
import os
import re
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0807_genre_draft"

raw = open(P, "rb").read()
crlf0, lf0 = raw.count(b"\r\n"), raw.count(b"\n")
print("修正前: CRLF %d / 単独LF %d" % (crlf0, lf0 - crlf0))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

t = raw.decode("utf-8")
changes, ng = [], []

# ① _genre の付け替え（fes は3888の1件だけ）
old = '    "_genre": "fes",\r\n'
if t.count(old) == 1:
    t = t.replace(old, '    "_genre": "classic",\r\n')
    changes.append("3888 南大阪オカリナフェスタ _genre fes → classic（会場が屋内）")
else:
    ng.append("3888 _genre fes のヒット数 %d" % t.count(old))

# ② _extraGenres の追加（エントリ内の最初の空配列だけを置換）
EXTRA = [
    (3896, "dinnershow", "3896 伊藤蘭 +dinnershow"),
    (3897, "dinnershow", "3897 鈴木雅之 +dinnershow"),
    (3913, "anime", "3913 オーケストラで聴くアニメ音楽の世界 +anime"),
    (3919, "dento", "3919 野村萬斎 with OEK +dento"),
    (3923, "anime", "3923 光が死んだ夏展 +anime"),
]
for eid, extra, label in EXTRA:
    m = re.search(r'\n    "id": %d,\n' % eid, t.replace("\r\n", "\n"))
    i = t.find('"id": %d,' % eid)
    if i < 0:
        ng.append(label + "（idが見つからない）")
        continue
    j = t.find('    "_extraGenres": [],\r\n', i)
    nxt = t.find('"id": ', i + 10)
    if j < 0 or (nxt > 0 and j > nxt):
        ng.append(label + "（エントリ内に空の_extraGenresが無い）")
        continue
    new = '    "_extraGenres": [\r\n     "%s"\r\n    ],\r\n' % extra
    t = t[:j] + new + t[j + len('    "_extraGenres": [],\r\n'):]
    changes.append(label)

b = t.encode("utf-8")
crlf1, lf1 = b.count(b"\r\n"), b.count(b"\n")
assert lf1 - crlf1 == lf0 - crlf0 == 0, "単独LFが混入した"
if ng:
    print("\n🚨 失敗があるので書き込まない:")
    for x in ng:
        print("  " + x)
    sys.exit(1)
open(P, "wb").write(b)
print("\n適用 %d件:" % len(changes))
for c in changes:
    print("  ✅ %s" % c)
print("修正後: CRLF %d / 単独LF %d" % (crlf1, lf1 - crlf1))
