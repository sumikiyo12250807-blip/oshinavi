# -*- coding: utf-8 -*-
"""既存エントリを新ジャンル「怪談」に反映する（ユーザーOK 2026-08-05「おねがい」）。

  A. 怪談そのものが主役 → genre を kaidan に移す（6件）
       44 稲川淳二 ／ 958 松原タニシの怪談七十物語 ／ 2737 松原タニシ44歳生誕祭
       1012 一龍斎貞鏡 秋日長怪談物語 ／ 2529・2530 今宵、怪談へ行く。
  B. 落語・寄席の怪談噺 → owarai のまま + extraGenres:["kaidan"]（6件）
       990 入船亭扇七 ／ 1049 大須演芸場8月定席 ／ 1053 立川小春志 ／
       1764 桂文我×三遊亭遊馬 ／ 1871 旭堂南龍 ／ 1992 桂文我 珍品怪談
     ＝落語ファンはお笑いから、怖い話目当ての人は怪談から辿り着ける（[[feedback_genre_both_when_unclear]]）

  ※ 2414 妖怪影絵劇「ゲゲゲの鬼太郎」は kids のまま＝怪談ではない（キーワードに引っかかっただけ）

index.html はバイナリで行単位に扱いCRLFを保つ（[[feedback_index_html_crlf_preserve]]）。
"""
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0805_kaidan_apply"

MOVE = [44, 958, 1012, 2529, 2530, 2737]          # genre → kaidan
BOTH = [990, 1049, 1053, 1764, 1871, 1992]        # genre据え置き + extraGenres:["kaidan"]

b = open(P, "rb").read()
crlf0, lf0 = b.count(b"\r\n"), b.count(b"\n")
print("修正前: CRLF %d / 単独LF %d" % (crlf0, lf0 - crlf0))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

lines = b.split(b"\r\n")
out = []
i = 0
done_move, done_both = [], []
targets = set(MOVE) | set(BOTH)
cur = None       # 処理中のエントリid
handled = set()

for idx, ln in enumerate(lines):
    s = ln.decode("utf-8", "replace")
    t = s.strip()
    if t.startswith('"id": '):
        try:
            cur = int(t[6:].rstrip(","))
        except ValueError:
            cur = None
    if cur in targets and cur not in handled and t.startswith('"genre": '):
        old = t.split(":", 1)[1].strip().rstrip(",").strip('"')
        if cur in MOVE:
            out.append('    "genre": "kaidan",'.encode("utf-8"))
            done_move.append((cur, old))
        else:
            out.append(ln)                                     # genreは据え置き
            out.append('    "extraGenres": ["kaidan"],'.encode("utf-8"))
            done_both.append((cur, old))
        handled.add(cur)
        continue
    out.append(ln)

miss = targets - handled
if miss:
    print("🚨 genre行が見つからなかったid: %s（1文字も書き込まない）" % sorted(miss))
    sys.exit(1)

nb = b"\r\n".join(out)
crlf1, lf1 = nb.count(b"\r\n"), nb.count(b"\n")
assert lf1 - crlf1 == 0, "単独LFが混入した"
open(P, "wb").write(nb)

print("\nA. 怪談へ移した %d件:" % len(done_move))
for i2, old in sorted(done_move):
    print("   id%-5d %s → kaidan" % (i2, old))
print("B. 両方方式にした %d件:" % len(done_both))
for i2, old in sorted(done_both):
    print("   id%-5d %s ＋ extraGenres:[kaidan]" % (i2, old))
print("\n修正後: CRLF %d / 単独LF %d" % (crlf1, lf1 - crlf1))
