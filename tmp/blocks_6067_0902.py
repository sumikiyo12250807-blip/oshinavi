# -*- coding: utf-8 -*-
"""id6067 t5 のURLの販売窓を実ページから全部出す。same[0] 決め打ちが疑わしいので確かめる。"""
import sys, json
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
from eplus_harvest import fetch
import reconcile_eplus as R

u = 'https://eplus.jp/sf/detail/4125060001-P0030013P021001'
html = fetch(u)
blocks = R.parse_blocks(html)
print('窓の数', len(blocks))
for b in blocks:
    print({k: (v.isoformat() if hasattr(v, 'isoformat') else v) for k, v in b.items()})
