# -*- coding: utf-8 -*-
"""e+の個別-P頁の販売窓を全部出す（引数=URL）。窓ズレFAILの実態確認用。"""
import sys
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
from eplus_harvest import fetch
import reconcile_eplus as R

u = sys.argv[1]
blocks = R.parse_blocks(fetch(u))
print(u)
print('窓の数', len(blocks))
for b in blocks:
    print({k: (v.isoformat() if hasattr(v, 'isoformat') else v) for k, v in b.items()})
