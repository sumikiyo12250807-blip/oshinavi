# -*- coding: utf-8 -*-
"""新ジャンル「グルメ」(gourmet) を新設する（2026-08-07・ユーザー選択③）。

きっかけ＝3926 ジャパン・ビアフェスティバル横浜2026 の行き先が無かった。
ぴあが会場の業態で「スクール・レジャー」を付けた結果 _genre が kids になっていたが、
ビール祭りは kids でないし、屋内なので fes の定義（複数組＋屋外）にも当てはまらない。
→ ビアフェス・食フェス・物産展の受け皿として新設する。

触るのは4か所（8/5に怪談を新設した時と同じ場所）:
  ① index.html  .filter-btn[data-genre] にボタン（イベントアートの次）
  ② index.html  バッジ色 .genre-gourmet（琥珀＝ビール色。既存のどの色とも重ならない明度にする）
  ③ index.html  GENRE_LABEL
  ④ tools/build_ai_page.py  GENRE_LABEL
GENRE_AMAZON_LINKS は**触らない**＝ジャンル汎用グッズはユーザー提供の amzn.to リンクが要るため
（怪談の時と同じ扱い。リンクをもらったら足す）。
"""
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

changes, ng = [], []


def patch(path, bak, edits):
    raw = open(path, "rb").read()
    crlf0, lf0 = raw.count(b"\r\n"), raw.count(b"\n")
    if not os.path.exists(bak):
        shutil.copyfile(path, bak)
    t = raw.decode("utf-8")
    for old, new, label in edits:
        if t.count(old) != 1:
            print("  🚨 %s: ヒット数 %d（1でないので中止）" % (label, t.count(old)))
            ng.append(label)
            continue
        t = t.replace(old, new)
        changes.append(label)
    b = t.encode("utf-8")
    crlf1, lf1 = b.count(b"\r\n"), b.count(b"\n")
    if lf0 - crlf0 == 0 and lf1 - crlf1 != 0:
        ng.append("%s に単独LFが混入" % path)
        return
    if ng:
        return
    open(path, "wb").write(b)
    print("  %s: CRLF %d → %d / 単独LF %d" % (os.path.basename(path), crlf0, crlf1, lf1 - crlf1))


IDX = r"C:\Users\user\oshinavi\index.html"
patch(IDX, r"C:\Users\user\oshinavi\index.html.bak_0807_genre_gourmet", [
    # ① フィルタボタン（イベントアートの次＝末尾）
    ('    <button class="filter-btn" data-genre="art">イベントアート</button>\r\n',
     '    <button class="filter-btn" data-genre="art">イベントアート</button>\r\n'
     '    <button class="filter-btn" data-genre="gourmet">グルメ</button>\r\n',
     "① フィルタボタン「グルメ」を追加（イベントアートの次）"),
    # ② バッジ色（琥珀）
    ('    .genre-dinnershow { background: rgba(217,138,160,0.15); color: #d98aa0;       border: 1px solid rgba(217,138,160,0.35); }\r\n',
     '    .genre-dinnershow { background: rgba(217,138,160,0.15); color: #d98aa0;       border: 1px solid rgba(217,138,160,0.35); }\r\n'
     '    .genre-gourmet    { background: rgba(232,163,61,0.15);  color: #e8a33d;       border: 1px solid rgba(232,163,61,0.35); }\r\n',
     "② バッジ色 .genre-gourmet（琥珀 #e8a33d）を追加"),
    # ③ GENRE_LABEL
    ('    aisatsu: "舞台挨拶", dinnershow: "ディナーショー", art: "イベントアート"\r\n',
     '    aisatsu: "舞台挨拶", dinnershow: "ディナーショー", art: "イベントアート",\r\n'
     '    gourmet: "グルメ"\r\n',
     "③ index.html の GENRE_LABEL に gourmet を追加"),
])

AIP = r"C:\Users\user\oshinavi\tools\build_ai_page.py"
patch(AIP, r"C:\Users\user\oshinavi\tools\build_ai_page.py.bak_0807", [
    ('    "art": "イベントアート", "kaidan": "怪談",\n',
     '    "art": "イベントアート", "kaidan": "怪談", "gourmet": "グルメ",\n',
     "④ build_ai_page.py の GENRE_LABEL に gourmet を追加"),
])

if ng:
    print("\n🚨 失敗があるので中止: %s" % " / ".join(ng))
    sys.exit(1)
print("\n適用 %d件:" % len(changes))
for c in changes:
    print("  ✅ %s" % c)
