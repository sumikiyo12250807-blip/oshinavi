# -*- coding: utf-8 -*-
"""新着プールの取りこぼし修正（id据え置き・現物編集）。
- 3523/3539/3541 に「受付中の先行枠」を追加（ぴあ再導出の実測値）
- 3519 の期限切れ枠(〜7/31 23:59)を削除
- 3539/3541 のツアー表記(venue/prefecture/dateLabel/date)をぴあ実態に合わせる
index.html はバイナリで読み書きし、挿入行もCRLFで書く＝改行に触らない。
並びは NEW_ORDER 固定なのでチェック位置は動かない（feedback_new_list_order_lock）。"""
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0801_newpool_miss"

b = open(P, "rb").read()
crlf0, lf0 = b.count(b"\r\n"), b.count(b"\n")
print("修正前: CRLF %d / 単独LF %d" % (crlf0, lf0 - crlf0))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)
    print("バックアップ: %s" % BAK)

changes = []


def rep(old, new, label):
    """1箇所だけ置換する（複数ヒットなら中止）"""
    global b
    o, n = old.encode("utf-8"), new.encode("utf-8")
    c = b.count(o)
    if c != 1:
        print("  🚨 %s: ヒット数 %d（1でないので中止）" % (label, c))
        return False
    b = b.replace(o, n)
    changes.append(label)
    return True


# ---- 3523 神戸国際taiko音楽祭2027：先行枠を追加 ----
rep(
    '      {\r\n'
    '        "type": "一般発売（兵庫 R9年 1/31公演）8/22 10:00発売",\r\n',
    '      {\r\n'
    '        "type": "先行（兵庫 R9年 1/31公演）〜8/12 11:00",\r\n'
    '        "date": "2026-08-12"\r\n'
    '      },\r\n'
    '      {\r\n'
    '        "type": "一般発売（兵庫 R9年 1/31公演）8/22 10:00発売",\r\n',
    "3523 先行枠を追加",
)

# ---- 3539 関取花：ツアー表記に修正＋先行枠を追加 ----
rep(
    '    "date": "2026-11-14",\r\n'
    '    "dateLabel": "2026年11月14日(土) 愛知 TOKUZO",\r\n'
    '    "venue": "TOKUZO",\r\n'
    '    "prefecture": "愛知",\r\n',
    '    "date": "2026-12-27",\r\n'
    '    "dateLabel": "2026年10月10日(土)〜2026年12月27日(日) 全国ツアー",\r\n'
    '    "venue": "全国ツアー（誰も知らない劇場／大手町三井ホール／Gioia Mia／TOKUZO／梅田BananaHall／Live Juke／栗林公園 商工奨励館／萬翠荘／ROOMS）",\r\n'
    '    "prefecture": "全国",\r\n',
    "3539 ツアー表記に修正",
)
rep(
    '      {\r\n'
    '        "type": "一般発売（愛知 11/14公演）8/22 10:00発売",\r\n',
    '      {\r\n'
    '        "type": "先行（宮城・東京・新潟・愛知・大阪・広島・香川・愛媛・福岡 10/10〜12/27公演）〜8/5 23:59",\r\n'
    '        "date": "2026-08-05"\r\n'
    '      },\r\n'
    '      {\r\n'
    '        "type": "一般発売（愛知 11/14公演）8/22 10:00発売",\r\n',
    "3539 先行枠を追加",
)

# ---- 3541 おとぼけビ～バ～：会場を補完＋先行枠を追加 ----
rep(
    '    "venue": "全国ツアー（名古屋クラブクアトロ／cube garden）",\r\n',
    '    "venue": "全国ツアー（cube garden／Spotify O-WEST／名古屋クラブクアトロ／Shangri-La）",\r\n',
    "3541 会場を補完",
)
rep(
    '      {\r\n'
    '        "type": "一般発売（愛知 9/14公演）8/15 10:00発売",\r\n',
    '      {\r\n'
    '        "type": "先行（東京・愛知・大阪 9/6〜9/14公演）〜8/9 23:59",\r\n'
    '        "date": "2026-08-09"\r\n'
    '      },\r\n'
    '      {\r\n'
    '        "type": "一般発売（愛知 9/14公演）8/15 10:00発売",\r\n',
    "3541 先行枠を追加",
)

crlf1, lf1 = b.count(b"\r\n"), b.count(b"\n")
assert lf1 - crlf1 == lf0 - crlf0 == 0, "単独LFが混入した"
open(P, "wb").write(b)

print("\n適用 %d件:" % len(changes))
for c in changes:
    print("  ✅ %s" % c)
print("修正後: CRLF %d / 単独LF %d" % (crlf1, lf1 - crlf1))
