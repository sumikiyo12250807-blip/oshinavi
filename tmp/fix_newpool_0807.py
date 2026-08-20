# -*- coding: utf-8 -*-
"""新着チェックで出た「枠の見分けがつかない」2件を、ぴあ実券種名に合わせて直す（2026-08-07）。

  3914 大河ドラマ「豊臣兄弟!」コンサート
       「プレイガイド最速先行」が締切違いで2枠あり、画面で区別できなかった。
       ぴあ実名は ①…※プレイガイド最速先行〈1階20列以内確約〉(〜8/9) ②プレイガイド最速先行(〜8/12)
  3925 Mozu ミニチュア展 岡山
       ぴあ実名は「一般発売＜当日券＞」なのに登録は「一般発売」。静岡は前売/当日を分けているのに岡山だけ無区別。

🚨 tickets の date は1つも動かさない＝新着リストの並び順を変えない（feedback_new_list_order_lock）。
index.html はバイナリで読み書きしCRLFを保つ。ヒット数が1でない置換は中止。
"""
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0807_newpool_fix"

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


rep(
    '        "type": "プレイガイド最速先行（東京 11/7公演）〜8/9 23:59",\r\n',
    '        "type": "プレイガイド最速先行〈1階20列以内確約〉（東京 11/7公演）〜8/9 23:59",\r\n',
    "3914 〜8/9の枠に〈1階20列以内確約〉を補って2枠を区別",
)
rep(
    '        "type": "一般発売（岡山 7/18〜8/30公演）〜8/30 16:00",\r\n',
    '        "type": "一般発売 当日券（岡山 7/18〜8/30公演）〜8/30 16:00",\r\n',
    "3925 岡山の枠を「一般発売 当日券」に訂正（ぴあ実名＜当日券＞）",
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
