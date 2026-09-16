# -*- coding: utf-8 -*-
"""check_expired の「⚠️要再確認」id と check_zero_badge の要対応 id と ヒールの隠れ枠 id の重なりを数える（読むだけ）。
使い方: python tmp/overlap_recheck_0911.py
出力: tmp/recheck_ids_0911.txt（要再確認のうちヒールが扱わないid・カンマ区切り）
"""
import re, sys, subprocess
sys.stdout.reconfigure(encoding='utf-8')

txt = open('tmp/check_expired_0911.txt', encoding='utf-8').read()
part = txt.split('⚠️ 以下は')[1] if '⚠️ 以下は' in txt else ''
recheck = [int(x) for x in re.findall(r'^  id=(\d+):', part, re.M)]

zb = subprocess.run(['node', 'tools/check_zero_badge.js', '--ids'], capture_output=True, text=True, encoding='utf-8')
zero = [int(x) for x in re.findall(r'\d+', zb.stdout.strip().splitlines()[-1])] if zb.stdout.strip() else []

print('要再確認', len(recheck), '/ バッジ0要対応', len(zero))
print('重なり(要再確認∩バッジ0)', len(set(recheck) & set(zero)))
print('バッジ0のうち要再確認に無い', len(set(zero) - set(recheck)))
open('tmp/recheck_ids_0911.txt', 'w', encoding='utf-8').write(','.join(map(str, sorted(set(recheck) | set(zero)))))
print('union', len(set(recheck) | set(zero)))
