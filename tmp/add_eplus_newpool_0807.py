# -*- coding: utf-8 -*-
"""新着50件のe+引き直しで見つかった「ぴあに無い枠」を足す（2026-08-07）。

  3926 ジャパン・ビアフェスティバル横浜2026
       ぴあは「8/19 10:00発売」だけ。e+は 8/1 から**もう受付中**＝今すぐ買える枠が4つ。
       同日に「お昼の回／午後の回」があるのでバッジに回を書く（feedback_same_day_show_time_badge）。
  3886 トンボコープ（宮城 9/27）
       e+「先着先行受付 〜9/3 18:00」受付中。ぴあのプリセール（〜9/3 23:59）とは締切が違う別枠。

🚨どちらも最早dateが変わらない＝新着リストの並び順は動かない（feedback_new_list_order_lock）。
   並び順が動く 3878 海援隊（e+プレオーダー8/18〜8/25）は振り分け後に回す。
index.html はバイナリで読み書きしCRLFを保つ。ヒット数が1でない置換は中止。
"""
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0807_eplus_newpool"

b = open(P, "rb").read()
crlf0, lf0 = b.count(b"\r\n"), b.count(b"\n")
print("修正前: CRLF %d / 単独LF %d" % (crlf0, lf0 - crlf0))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

changes, ng = [], []


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


EP = "https://eplus.jp/sf/detail/4576960001-P0030001%s"

# ============ 3926 ジャパン・ビアフェスティバル横浜2026 ============
old = tk("一般発売（神奈川 9/12〜9/13公演）8/19 10:00発売", "2026-08-19",
         start="2026-08-19", last=True)
new = tk("一般発売（神奈川 9/12〜9/13公演）8/19 10:00発売", "2026-08-19", start="2026-08-19")
new += tk("一般発売＜お昼の回＞（神奈川 9/12公演）〜9/11 23:59", "2026-09-11", url=EP % "P021001")
new += tk("一般発売＜午後の回＞（神奈川 9/12公演）〜9/11 23:59", "2026-09-11", url=EP % "P021002")
new += tk("一般発売＜お昼の回＞（神奈川 9/13公演）〜9/12 23:59", "2026-09-12", url=EP % "P021003")
new += tk("一般発売＜午後の回＞（神奈川 9/13公演）〜9/12 23:59", "2026-09-12",
          url=EP % "P021004", last=True)
rep(old, new, "3926 e+の4枠（9/12・9/13の昼/午後・もう受付中）を追加")

# ============ 3886 トンボコープ（宮城 9/27） ============
rep(
    tk("プリセール（宮城 9/27公演）〜9/3 23:59", "2026-09-03"),
    tk("プリセール（宮城 9/27公演）〜9/3 23:59", "2026-09-03")
    + tk("先着先行受付（宮城 9/27公演）〜9/3 18:00", "2026-09-03",
         url="https://eplus.jp/sf/detail/4037240001-P0030022P021001"),
    "3886 e+の先着先行受付（〜9/3 18:00・受付中）を追加",
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
