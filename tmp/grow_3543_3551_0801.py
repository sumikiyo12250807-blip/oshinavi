# -*- coding: utf-8 -*-
"""id3543 シンガーズハイ / id3551 髪結いの亭主 に、監査で見つかった枠だけを足す。
🚨 grow_from_audit --apply は使わない（EXILEの誤マージ・真心の枠消失を巻き込むため）。
既存の枠（特に3543の日本武道館 11/24）は1つも消さない。
index.html はバイナリで読み書きし、挿入行もCRLFで書く。並びは NEW_ORDER 固定。"""
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0801_grow_3543_3551"
U = "https://t.pia.jp/pia/event/event.do?eventCd="

b = open(P, "rb").read()
crlf0, lf0 = b.count(b"\r\n"), b.count(b"\n")
print("修正前: CRLF %d / 単独LF %d" % (crlf0, lf0 - crlf0))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

changes = []


def rep(old, new, label):
    global b
    o, n = old.encode("utf-8"), new.encode("utf-8")
    c = b.count(o)
    if c != 1:
        print("  🚨 %s: ヒット数 %d（1でないので中止）" % (label, c))
        return False
    b = b.replace(o, n)
    changes.append(label)
    return True


def tk(type_, date, url, start=None):
    s = '      {\r\n        "type": "%s",\r\n        "date": "%s",\r\n' % (type_, date)
    if start:
        s += '        "startDate": "%s",\r\n' % start
    s += '        "url": "%s"\r\n      },\r\n' % url
    return s


# ================= 3543 シンガーズハイ =================
# ツアー表記を7会場＋武道館に更新（武道館は絶対に落とさない）
rep(
    '    "dateLabel": "2026年10月9日(金)〜2026年11月24日(火) 全国ツアー",\r\n'
    '    "venue": "全国ツアー（仙台Rensa／日本武道館／Zepp Fukuoka）",\r\n',
    '    "dateLabel": "2026年9月8日(火)〜2026年11月24日(火) 全国ツアー",\r\n'
    '    "venue": "全国ツアー（KT Zepp Yokohama／ペニーレーン24／高松festhalle／広島クラブクアトロ／Zepp Osaka Bayside／仙台Rensa／Zepp Fukuoka／日本武道館）",\r\n',
    "3543 ツアー表記を8会場に更新",
)

# 新規5枠を tickets の先頭に挿入（既存3枠はそのまま）
anchor3543 = (
    '    "tickets": [\r\n'
    '      {\r\n'
    '        "type": "プレリザーブ（福岡 10/16公演）8/1 12:00発売",\r\n'
)
add3543 = (
    '    "tickets": [\r\n'
    + tk("プレリザーブ（大阪 10/1公演）〜8/4 23:59", "2026-08-04", U + "2621199")
    + tk("プレリザーブ（北海道 9/15公演）8/4 11:00発売", "2026-08-06", U + "2620113", "2026-08-04")
    + tk("プリセール（神奈川 9/8公演）〜8/6 23:59", "2026-08-06", U + "2630664")
    + tk("プリセール（香川 9/26公演）〜8/6 23:59", "2026-08-06", U + "2630693")
    + tk("プリセール（広島 9/27公演）〜8/6 23:59", "2026-08-06", U + "2630700")
    + '      {\r\n'
      '        "type": "プレリザーブ（福岡 10/16公演）8/1 12:00発売",\r\n'
)
rep(anchor3543, add3543, "3543 未登録5枠を追加")

# ================= 3551 髪結いの亭主 =================
rep(
    '    "dateLabel": "2026年11月5日(木)〜2026年11月6日(金) 広島 広島JMSアステールプラザ 大ホール",\r\n'
    '    "venue": "広島JMSアステールプラザ 大ホール",\r\n'
    '    "prefecture": "広島",\r\n',
    '    "dateLabel": "2026年9月28日(月)〜2026年11月6日(金) 全国ツアー",\r\n'
    '    "venue": "全国ツアー（新国立劇場 小劇場／広島JMSアステールプラザ 大ホール）",\r\n'
    '    "prefecture": "全国",\r\n',
    "3551 ツアー表記に更新",
)
rep(
    '      {\r\n'
    '        "type": "一般発売（広島 11/5〜11/6公演）8/22 10:00発売",\r\n'
    '        "date": "2026-08-22",\r\n'
    '        "startDate": "2026-08-22"\r\n'
    '      }\r\n',
    '      {\r\n'
    '        "type": "一般発売（東京 9/28〜10/25公演）8/22 10:00発売",\r\n'
    '        "date": "2026-08-22",\r\n'
    '        "startDate": "2026-08-22",\r\n'
    '        "url": "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670167"\r\n'
    '      },\r\n'
    '      {\r\n'
    '        "type": "一般発売（広島 11/5〜11/6公演）8/22 10:00発売",\r\n'
    '        "date": "2026-08-22",\r\n'
    '        "startDate": "2026-08-22",\r\n'
    '        "url": "https://t.pia.jp/pia/event/event.do?eventCd=2628760"\r\n'
    '      }\r\n',
    "3551 東京ロングランを追加",
)

crlf1, lf1 = b.count(b"\r\n"), b.count(b"\n")
assert lf1 - crlf1 == lf0 - crlf0 == 0, "単独LFが混入した"
open(P, "wb").write(b)
print("\n適用 %d件:" % len(changes))
for c in changes:
    print("  ✅ %s" % c)
print("修正後: CRLF %d / 単独LF %d" % (crlf1, lf1 - crlf1))
