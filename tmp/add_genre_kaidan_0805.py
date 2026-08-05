# -*- coding: utf-8 -*-
"""新ジャンル「怪談」(kaidan)をOSHINAVIに追加する（ユーザー指示 2026-08-04夜「怪談を作って」）。

触るのは3か所:
  ① index.html の `.filter-btn[data-genre]` ＝フィルタボタン（お笑いの次に置く）
  ② index.html の `GENRE_LABEL`           ＝カードのジャンルタグ表示名
  ③ tools/build_ai_page.py の `GENRE_LABEL` ＝AIページ/SSR側（enka・dento・artの取りこぼしも一緒に補う）

`GENRE_AMAZON_LINKS`（ジャンル汎用グッズボタン）は amzn.to のリンクがユーザー提供物なので今回は触らない。
index.html はバイナリで読み書きしCRLFを保つ（[[feedback_index_html_crlf_preserve]]）。
"""
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

IDX = r"C:\Users\user\oshinavi\index.html"
AIP = r"C:\Users\user\oshinavi\tools\build_ai_page.py"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0805_genre_kaidan"

changes, ng = [], []


def rep_bin(path, old, new, label):
    b = open(path, "rb").read()
    o, n = old.encode("utf-8"), new.encode("utf-8")
    c = b.count(o)
    if c != 1:
        print("  🚨 %s: ヒット数 %d（1でないので中止）" % (label, c))
        ng.append(label)
        return None
    return b.replace(o, n)


# ===== index.html =====
b = open(IDX, "rb").read()
crlf0, lf0 = b.count(b"\r\n"), b.count(b"\n")
print("index.html 修正前: CRLF %d / 単独LF %d" % (crlf0, lf0 - crlf0))
if not os.path.exists(BAK):
    shutil.copyfile(IDX, BAK)


def rep(old, new, label):
    global b
    o, n = old.encode("utf-8"), new.encode("utf-8")
    c = b.count(o)
    if c != 1:
        print("  🚨 %s: ヒット数 %d（1でないので中止）" % (label, c))
        ng.append(label)
        return False
    b = b.replace(o, n)
    changes.append(label)
    return True


# ① フィルタボタン（.filter-btn[data-genre] の形を守る＝[[feedback_filter_selector]]）
rep(
    '    <button class="filter-btn" data-genre="owarai">お笑い</button>\r\n',
    '    <button class="filter-btn" data-genre="owarai">お笑い</button>\r\n'
    '    <button class="filter-btn" data-genre="kaidan">怪談</button>\r\n',
    "① フィルタボタン「怪談」を追加（お笑いの次）",
)

# ② GENRE_LABEL
rep(
    '    classic: "クラシック", jazz: "ジャズ", enka: "演歌", dento: "伝統",\r\n',
    '    classic: "クラシック", jazz: "ジャズ", enka: "演歌", dento: "伝統",\r\n'
    '    kaidan: "怪談",\r\n',
    "② GENRE_LABEL に kaidan:「怪談」を追加",
)

crlf1, lf1 = b.count(b"\r\n"), b.count(b"\n")
assert lf1 - crlf1 == lf0 - crlf0 == 0, "単独LFが混入した"

# ===== tools/build_ai_page.py（enka/dento/art の欠落も補う） =====
nb = rep_bin(
    AIP,
    '    "owarai": "お笑い", "musical": "ミュージカル", "aisatsu": "舞台挨拶",\r\n'
    '    "dinnershow": "ディナーショー",\r\n',
    '    "owarai": "お笑い", "musical": "ミュージカル", "aisatsu": "舞台挨拶",\r\n'
    '    "dinnershow": "ディナーショー", "enka": "演歌", "dento": "伝統",\r\n'
    '    "art": "イベントアート", "kaidan": "怪談",\r\n',
    "③ build_ai_page.py の GENRE_LABEL に kaidan＋欠落(enka/dento/art)を追加",
)
if nb is not None:
    changes.append("③ build_ai_page.py の GENRE_LABEL に kaidan＋欠落(enka/dento/art)を追加")

if ng:
    print("\n🚨 失敗があるので1文字も書き込まない: %s" % " / ".join(ng))
    sys.exit(1)

open(IDX, "wb").write(b)
open(AIP, "wb").write(nb)
print("\n適用 %d件:" % len(changes))
for c in changes:
    print("  ✅ %s" % c)
print("index.html 修正後: CRLF %d / 単独LF %d" % (crlf1, lf1 - crlf1))
