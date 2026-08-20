# -*- coding: utf-8 -*-
"""genre=engeki の各エントリが「ぴあのカテゴリ(_piaSub)」を持っているかを数える。
持っていれば機械で振り直せる。持っていなければ何を根拠にするか要検討。"""
import os, sys, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
from check_expired import extract_events_array
sys.stdout.reconfigure(encoding='utf-8')

ev = [e for e in extract_events_array('index.html') if e.get('verified') is True]
eng = [e for e in ev if e.get('genre') == 'engeki']
has = [e for e in eng if e.get('_piaSub')]
non = [e for e in eng if not e.get('_piaSub')]
print('genre=engeki %d件 / _piaSubあり %d件 / なし %d件' % (len(eng), len(has), len(non)))
print('\n--- _piaSub の内訳（ありの分）---')
for k, n in collections.Counter(e['_piaSub'] for e in has).most_common():
    print('  %-34s %3d' % (k, n))
print('\n--- _piaSub が無い %d件のうち先頭40件 ---' % len(non))
for e in non[:40]:
    print('  %d\t%s' % (e['id'], (e.get('name') or '')[:50]))
