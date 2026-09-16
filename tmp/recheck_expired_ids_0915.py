# -*- coding: utf-8 -*-
"""check_expired の「⚠️要再確認」と、check_zero_badge の「要対応（31日より先で枠0）」の id を合わせて、
reconcile_pia --ids に渡す一覧を作る（読むだけ・2026-09-15 朝）。
使い方: python tmp/recheck_expired_ids_0915.py
入力: tmp/expired_0915.txt ／ tmp/zerobadge_ids_0915.txt
出力: tmp/recon_ids_0915.txt（カンマ区切り）
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
txt = io.open('tmp/expired_0915.txt', encoding='utf-8').read()
pos = txt.find('⚠️ 以下は')
rec = [int(x) for x in re.findall(r'^  id=(\d+):', txt[pos:], re.M)] if pos >= 0 else []
zb = [int(x) for x in re.findall(r'\d+', io.open('tmp/zerobadge_ids_0915.txt', encoding='utf-8').read().split('\n')[0])]
both = sorted(set(rec) | set(zb))
io.open('tmp/recon_ids_0915.txt', 'w', encoding='utf-8').write(','.join(str(i) for i in both))
print('要再確認 %d件 ／ 番人の要対応 %d件 ／ 重なり %d件 ／ 合わせて %d件 → tmp/recon_ids_0915.txt' % (
    len(rec), len(zb), len(set(rec) & set(zb)), len(both)))
