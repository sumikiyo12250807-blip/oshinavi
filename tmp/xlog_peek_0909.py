# -*- coding: utf-8 -*-
"""x_log.json に貯めてあるフォロワー数を、今日の候補と突き合わせる。"""
import io, json, sys
sys.stdout.reconfigure(encoding='utf-8')

d = json.load(io.open('tools/x_log.json', encoding='utf-8'))
print('トップのキー:', list(d.keys()))
for k, v in d.items():
    if isinstance(v, dict):
        print('  %s = dict %d件  例: %s' % (k, len(v), list(v.items())[:3]))
    elif isinstance(v, list):
        print('  %s = list %d件  例: %s' % (k, len(v), v[:2]))
    else:
        print('  %s = %r' % (k, v))
