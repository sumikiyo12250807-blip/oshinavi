# -*- coding: utf-8 -*-
"""今朝の新着50件(3731-3780)をレビューして見つかった2件を直す（2026-08-05 昼）。

  3769 ルパン三世(南座) … 5枠目がぴあでは「≪3階左右列見切れ席≫」なのに4枠目と完全同一表記
                          ＝画面で見分けがつかない。席種ラベルを復元する。
  3745 海蔵亮太          … 県の並びが日付順と逆（北海道10/18 → 東京11/11 なのに「東京・北海道」）。

index.html はバイナリで読み書きしCRLFを保つ（[[feedback_index_html_crlf_preserve]]）。
ヒット数が1でない置換は中止。
"""
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0805_newpool_fix"

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


# ===== 3769 席種ラベルの復元（2つ並んだ同一枠の後ろ側だけを直す） =====
blk = (
    '      {\r\n'
    '        "type": "%s",\r\n'
    '        "date": "2026-08-09",\r\n'
    '        "startDate": "2026-08-09"\r\n'
    '      }'
)
same = "一般発売（京都 9/2〜9/26公演）8/9 10:00発売"
labeled = "一般発売≪3階左右列見切れ席≫（京都 9/2〜9/26公演）8/9 10:00発売"
rep(
    (blk % same) + ",\r\n" + (blk % same),
    (blk % same) + ",\r\n" + (blk % labeled),
    "3769 5枠目に席種≪3階左右列見切れ席≫を復元",
)

# ===== 3745 県の並びを日付順に =====
rep(
    '    "dateLabel": "2026年10月18日(日)〜2026年11月11日(水) 東京・北海道",\r\n'
    '    "venue": "全国ツアー（SHIBUYA PLEASURE PLEASURE／VyPass.）",\r\n'
    '    "prefecture": "東京・北海道",\r\n',
    '    "dateLabel": "2026年10月18日(日)〜2026年11月11日(水) 北海道・東京",\r\n'
    '    "venue": "全国ツアー（VyPass.／SHIBUYA PLEASURE PLEASURE）",\r\n'
    '    "prefecture": "北海道・東京",\r\n',
    "3745 県・会場の並びを公演日順に",
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
