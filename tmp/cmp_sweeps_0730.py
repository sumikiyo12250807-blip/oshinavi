# -*- coding: utf-8 -*-
"""rlsIn=03 と rlsIn=04 のスイープ結果を比べる。04が本当に「発売がもっと先」を返しているか確認。"""
import collections
import json
import re

TAGS = ['music', 'engeki', 'classic', 'art', 'event', 'sports']
out = []


def cds(items):
    s = set()
    for it in items:
        m = re.search(r'event(?:Bundle)?Cd=(\w+)', it.get('url') or '')
        if m:
            s.add(m.group(1))
    return s


for tag in TAGS:
    d3 = d4 = None
    try:
        d3 = json.load(open(f'tmp/presale_{tag}03_0730.json', encoding='utf-8'))
    except Exception as e:
        out.append(f'{tag}: 03 読めない {e}')
    try:
        d4 = json.load(open(f'tmp/presale_{tag}04_0730.json', encoding='utf-8'))
    except Exception as e:
        out.append(f'{tag}: 04 読めない {e}')
    if not (d3 and d4):
        continue
    n3, n4 = d3.get('new', []), d4.get('new', [])
    c3, c4 = cds(n3), cds(n4)
    out.append(f'{tag}: 03未掲載{len(n3)}件(cd{len(c3)}) / 04未掲載{len(n4)}件(cd{len(c4)}) / 共通cd {len(c3 & c4)}')
    r3 = collections.Counter((it.get('rlsdate') or '(空)')[:7] for it in n3)
    r4 = collections.Counter((it.get('rlsdate') or '(空)')[:7] for it in n4)
    out.append(f'    03 rlsdate内訳: {dict(sorted(r3.items()))}')
    out.append(f'    04 rlsdate内訳: {dict(sorted(r4.items()))}')
    # 全体件数(未掲載でなく総数)も見る
    out.append(f'    03 total={d3.get("total")} 04 total={d4.get("total")}  keys={sorted(d3.keys())}')

open('tmp/cmp_sweeps_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/cmp_sweeps_0730.txt')
