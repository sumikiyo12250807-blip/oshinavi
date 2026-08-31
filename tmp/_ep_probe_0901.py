# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0,'tools'); sys.stdout.reconfigure(encoding='utf-8')
from eplus_harvest import fetch, parse_ld, parse_windows
for u in ['https://eplus.jp/sf/detail/4531630001-P0030001P021001',
          'https://eplus.jp/sf/detail/4531580001-P0030001P021001',
          'https://eplus.jp/sf/detail/4125060001-P0030013P021001',
          'https://eplus.jp/sf/detail/4306490002']:
    h=fetch(u)
    print('===',u)
    for ev in parse_ld(h): print('  LD', ev.get('date'), ev.get('time'), '|', ev.get('venue'), '|', ev.get('pref'), '|', ev.get('name'))
    for w in parse_windows(h): print('  W ', w.get('kind'), '|', w.get('label'), '| sd', w.get('sd'), w.get('st'), '| ed', w.get('ed'), w.get('et'))
