# -*- coding: utf-8 -*-
"""id3696 Stray Kids の枠名を、ぴあの実際の券種名に合わせて直す（2026-08-05・ユーザー指摘）。

ユーザー「Stray Kids World Tourのセブンはoshinavi.jpにのってない」＝
**枠自体は登録されているが、名前が「先行【全国】」なのでセブン-イレブン先行だと分からない**。
X投稿で「8/12はセブン-イレブン先行」と書いて oshinavi.jp へ誘導するのに、
着いた先でそれが分からないのは案内として成立しない（[[feedback_no_fake_info]]／[[feedback_oshikatsu_first]]）。

ぴあの実際の券種名（b2670074 を機械パースして確認）:
  ■Stray Kids（全国）※ぴあNICOSカード限定   8/7(金)20:00 〜 8/11(火・祝)23:59
  Stray Kids〔全国〕※セブン-イレブン先行     8/12(水)12:00 〜 8/16(日)23:59
→ 「先行」「先行【全国】」では**誰が買えるのかが伝わらない**ので券種名を反映する。
   日付(date/startDate)は既に正しいので触らない。
"""
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0805_straykids_names"

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
    changes.append((label, old.strip(), new.strip()))
    return True


rep(
    '        "type": "先行（東京・愛知・大阪・福岡 8/29〜10/24公演）8/7 20:00発売",\r\n',
    '        "type": "ぴあNICOSカード限定先行（東京・愛知・大阪・福岡 8/29〜10/24公演）8/7 20:00発売",\r\n',
    "8/7の枠＝ぴあNICOSカード限定と明記",
)
rep(
    '        "type": "先行【全国】（東京・愛知・大阪・福岡 8/29〜10/24公演）8/12 12:00発売",\r\n',
    '        "type": "セブン-イレブン先行（東京・愛知・大阪・福岡 8/29〜10/24公演）8/12 12:00発売",\r\n',
    "8/12の枠＝セブン-イレブン先行と明記",
)

crlf1, lf1 = b.count(b"\r\n"), b.count(b"\n")
assert lf1 - crlf1 == lf0 - crlf0 == 0, "単独LFが混入した"
if ng:
    print("\n🚨 失敗があるので書き込まない: %s" % " / ".join(ng))
    sys.exit(1)
open(P, "wb").write(b)
print("\n適用 %d件:" % len(changes))
for label, o, n in changes:
    print("  ✅ %s" % label)
print("修正後: CRLF %d / 単独LF %d" % (crlf1, lf1 - crlf1))
