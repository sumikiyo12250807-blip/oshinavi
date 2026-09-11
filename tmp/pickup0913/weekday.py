# -*- coding: utf-8 -*-
"""記事の「日付(曜日)」を実カレンダーと照合する（読むだけ）。
年の書いていない日付は、9〜12月＝2026年、1〜8月＝2027年として見る（例外は本文に年が書いてある所）。"""
import datetime, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
W = '月火水木金土日'
d = io.open('tmp/pickup0913/draft.md', encoding='utf-8').read()
bad = n = 0
pat = re.compile(r'(?:(20\d\d)年)?(\d{1,2})[/月](\d{1,2})日?\s*[（(]([月火水木金土日])')
for m in pat.finditer(d):
    y, mo, dd, w = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4)
    y = int(y) if y else (2026 if mo >= 8 else 2027)
    real = W[datetime.date(y, mo, dd).weekday()]
    n += 1
    if real != w:
        bad += 1
        print('❌', m.group(0), '→ 正しくは', real)
# 「2日（土）」のように月を省いた形（直前の月を引き継ぐ）
for m in re.finditer(r'2027年1月1日（金・祝）、2日（([月火水木金土日])）、3日（([月火水木金土日])）', d):
    for day, w in ((2, m.group(1)), (3, m.group(2))):
        n += 1
        if W[datetime.date(2027, 1, day).weekday()] != w:
            bad += 1
            print('❌ 1/%d(%s)' % (day, w))
# 「12/22(火)・23(水)」の形
for m in re.finditer(r'(\d{1,2})/(\d{1,2})\(([月火水木金土日])\)・(\d{1,2})\(([月火水木金土日])\)', d):
    mo = int(m.group(1)); y = 2026 if mo >= 8 else 2027
    n += 1
    if W[datetime.date(y, mo, int(m.group(4))).weekday()] != m.group(5):
        bad += 1
        print('❌', m.group(0))
print('曜日 %d か所を照合 → ずれ %d' % (n, bad))
