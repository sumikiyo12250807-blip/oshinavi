# -*- coding: utf-8 -*-
"""expired レポートから id 群を抽出して2群に分ける（削除候補 / 要再確認）"""
import re, io, sys

txt = io.open('tmp/expired_0817.txt', encoding='utf-8').read()

# セクション分割: 「期限切れ削除候補(公演終了済)」の行群 と 「⚠️要再確認」の行群
lines = txt.split('\n')
mode = None
dele, recheck = [], []
for ln in lines:
    if ln.startswith('[削除候補') or '期限切れ削除候補' in ln and ln.strip().startswith('##'):
        pass
    m = re.match(r'^\s*id=(\d+):', ln)
    if ln.strip().startswith('===') or ln.strip().startswith('---'):
        continue
    if '要再確認' in ln and 'id=' not in ln:
        mode = 'recheck'
        continue
    if '削除候補' in ln and 'id=' not in ln and '要再確認' not in ln:
        mode = 'delete'
        continue
    if m:
        (recheck if mode == 'recheck' else dele).append((int(m.group(1)), ln.strip()))

print('=== DELETE候補(公演終了済) %d件 ===' % len(dele))
print(','.join(str(i) for i, _ in dele))
print()
print('=== 要再確認 %d件 ===' % len(recheck))
print(','.join(str(i) for i, _ in recheck))
