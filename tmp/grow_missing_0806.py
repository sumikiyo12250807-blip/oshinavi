# -*- coding: utf-8 -*-
"""8/6朝の reconcile で出た取りこぼし・救済3件にぴあ実枠を足す。

  1066 劇団☆新感線『アケチコ！』 ＝ 当日引換券（福岡 7/24〜8/8公演）〜8/7 8:30 が欠落（受付中）
  1593 LADYBABY               ＝ プレリザーブ2次（東京 12/1公演）〜8/16 23:59 が欠落（受付中）
  1040 三谷文楽『人形ぎらい』      ＝ 券種ページに「8/7(金)10:00より販売再開」＝発売前枠を追加

index.html はバイナリで読み書きしCRLFを保つ（[[feedback_index_html_crlf_preserve]]）。
既存枠は1つも消さない。ヒット数が1でない置換は中止。
"""
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0806_grow_missing"

b = open(P, "rb").read()
crlf0, lf0 = b.count(b"\r\n"), b.count(b"\n")
print("修正前: CRLF %d / 単独LF %d" % (crlf0, lf0 - crlf0))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

changes = []
ng = []


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


def tk(type_, date, start=None, url=None, last=False):
    s = '      {\r\n        "type": "%s",\r\n        "date": "%s"' % (type_, date)
    if start:
        s += ',\r\n        "startDate": "%s"' % start
    if url:
        s += ',\r\n        "url": "%s"' % url
    s += "\r\n      }" + ("\r\n" if last else ",\r\n")
    return s


# ============ 1066 劇団☆新感線『アケチコ！』 当日引換券 ============
rep(
    tk("一般発売（福岡 7/24〜8/8公演）〜8/5 23:59", "2026-08-05", last=True),
    tk("一般発売（福岡 7/24〜8/8公演）〜8/5 23:59", "2026-08-05")
    + tk("当日引換券（福岡 7/24〜8/8公演）〜8/7 8:30", "2026-08-07", last=True),
    "1066 当日引換券（福岡 7/24〜8/8公演）〜8/7 8:30 を追加",
)

# ============ 1593 LADYBABY プレリザーブ2次 ============
rep(
    tk("抽選プレオーダー受付（東京 12/1公演）〜8/5 18:00", "2026-08-05",
       url="https://eplus.jp/sf/detail/1994490001-P0030049P021001", last=True),
    tk("抽選プレオーダー受付（東京 12/1公演）〜8/5 18:00", "2026-08-05",
       url="https://eplus.jp/sf/detail/1994490001-P0030049P021001")
    + tk("プレリザーブ2次（東京 12/1公演）〜8/16 23:59", "2026-08-16",
         url="https://t.pia.jp/pia/event/event.do?eventCd=2621504", last=True),
    "1593 プレリザーブ2次（東京 12/1公演）〜8/16 23:59 を追加",
)

# ============ 1040 三谷文楽『人形ぎらい』 8/7 10:00 販売再開 ============
rep(
    tk("一般発売（京都 8/21〜8/26公演）〜8/5 23:59", "2026-08-05", last=True),
    tk("一般発売（京都 8/21〜8/26公演）〜8/5 23:59", "2026-08-05")
    + tk("一般発売（京都 8/21〜8/26公演）8/7 10:00発売", "2026-08-07",
         start="2026-08-07", last=True),
    "1040 一般発売（8/7 10:00 販売再開）を追加",
)

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
