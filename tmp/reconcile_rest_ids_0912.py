# -*- coding: utf-8 -*-
"""途中で止めたぴあ照合（tmp/reconcile_recheck_0912.txt）から、照合し終えた id を数えて、
残りの id を昼の続き用に書き出す（読むだけ）。
朝は発売前スイープを優先するため 07:55 ごろ止めた（ぴあを並べて叩くと混雑ページで両方が崩れる）。
使い方: python tmp/reconcile_rest_ids_0912.py
出力: tmp/reconcile_ids_rest_0912.txt（カンマ区切り）
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
allids = [int(x) for x in io.open('tmp/reconcile_ids_0912.txt', encoding='utf-8').read().split(',') if x.strip()]
txt = io.open('tmp/reconcile_recheck_0912.txt', encoding='utf-8', errors='replace').read()
done = {int(m.group(1)) for m in re.finditer(r'^(?:✅|🚨|❌|⚠️|⏭️?)\s*id=(\d+)\s', txt, re.M)}
rest = [i for i in allids if i not in done]
io.open('tmp/reconcile_ids_rest_0912.txt', 'w', encoding='utf-8').write(','.join(map(str, rest)))
print('対象 %d件 ／ 照合し終えた %d件 ／ 残り %d件 → tmp/reconcile_ids_rest_0912.txt' % (len(allids), len(done), len(rest)))
