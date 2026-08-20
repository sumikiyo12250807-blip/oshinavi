# -*- coding: utf-8 -*-
"""genre=engeki のうち、名前に「ミュージカル」が入っているものと入っていないものを数える。
（表示名を「ミュージカル」に変えた影響がどれだけ嘘になるかの実測）"""
import os, sys, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
from check_expired import extract_events_array
sys.stdout.reconfigure(encoding='utf-8')

ev = [e for e in extract_events_array('index.html') if e.get('verified') is True]
eng = [e for e in ev if e.get('genre') == 'engeki']
mus = [e for e in ev if e.get('genre') == 'musical']
hit = [e for e in eng if 'ミュージカル' in (e.get('name') or '') or 'ミュージカル' in (e.get('artist') or '')]
miss = [e for e in eng if e not in hit]
print('genre=engeki %d件 / genre=musical %d件' % (len(eng), len(mus)))
print('  うち名前に「ミュージカル」あり: %d件' % len(hit))
print('  名前に無い: %d件' % len(miss))
print('\n--- 名前に「ミュージカル」が無い engeki の例（先頭30件）---')
for e in miss[:30]:
    print('  %d\t%s' % (e['id'], (e.get('name') or '')[:52]))
