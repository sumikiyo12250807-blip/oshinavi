# -*- coding: utf-8 -*-
"""3075/3090 のe+ツアー全公演を列挙する（JSON-LD源）"""
import sys, io, json
sys.path.insert(0, 'tools')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from eplus_harvest import fetch, parse_ld

TARGETS = [
    ('3075 ほんわかあもんぴーず', 'https://eplus.jp/sf/detail/3830670001-P0030011P021001'),
    ('3090 Lavt', 'https://eplus.jp/sf/detail/4247640001-P0030009P021001'),
]

for label, url in TARGETS:
    print('=' * 60)
    print(label, url)
    html = fetch(url)
    if not html:
        print('  FETCH FAIL')
        continue
    ld = parse_ld(html)
    print('  parse_ld ->', json.dumps(ld, ensure_ascii=False)[:4000])
