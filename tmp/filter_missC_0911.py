# -*- coding: utf-8 -*-
"""id353 SPY×FAMILY（ツアー全体）の組み直しから愛知の枠を外す。愛知・御園座は id4615 に割れて登録済み＝二重に出さない。"""
import io, json, sys
sys.stdout.reconfigure(encoding='utf-8')
P = 'tmp/built_missC_0911.json'
d = json.load(io.open(P, encoding='utf-8-sig'))
for b in d:
    if b['id'] == 353:
        before = len(b['tickets'])
        b['tickets'] = [t for t in b['tickets'] if '（愛知 ' not in t['type']]
        print('353: %d → %d枠' % (before, len(b['tickets'])))
json.dump(d, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
