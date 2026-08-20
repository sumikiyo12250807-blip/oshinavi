# -*- coding: utf-8 -*-
"""⚠️相談の3件を NEW_ORDER の先頭へ（memory: feedback_new_order_array / feedback_consultation_mark）。
残りは投入順(id昇順)のまま。EVENTS配列には触らない。"""
import re, sys, json
sys.stdout.reconfigure(encoding='utf-8')

CONSULT = [4259, 4260, 4258]   # 台湾開催 / ジャンル下書きがkids誤り / ファンミのジャンル
h = open('index.html', encoding='utf-8', newline='').read()
mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
assert mo, 'NEW_ORDER が見つからない'
cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
assert all(i in cur for i in CONSULT), '相談idがNEW_ORDERに無い'
new = CONSULT + [i for i in cur if i not in CONSULT]
assert sorted(new) == sorted(cur), '件数が変わった'
h2, n = re.subn(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]',
                lambda m: m.group(1) + '[' + ', '.join(str(i) for i in new) + ']', h, count=1)
assert n == 1
open('index.html', 'w', encoding='utf-8', newline='').write(h2)
print('NEW_ORDER %d件 / 先頭3件=%s' % (len(new), new[:3]))
