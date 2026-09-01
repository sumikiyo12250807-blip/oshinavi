# -*- coding: utf-8 -*-
import sys, re, html as H, time
sys.path.insert(0,'tools'); sys.stdout.reconfigure(encoding='utf-8')
from eplus_harvest import fetch, parse_ld, parse_windows
h = fetch('https://eplus.jp/sf/word/0000168060')
urls = sorted(set('https://eplus.jp/sf/detail/'+u for u in re.findall(r'/sf/detail/(\d{10}-P\d+P\d+)', h)))
for u in urls:
    hh = fetch(u); time.sleep(0.4)
    ld = parse_ld(hh); ws = parse_windows(hh)
    print('==', u)
    for e in ld: print('   公演', e.get('date'), e.get('time'), '|', e.get('venue'), '|', e.get('pref'), '|', (e.get('name') or '')[:60])
    for w in ws: print('   枠  ', w.get('label'), '| 開始', w.get('sd'), w.get('st'), '| 締切', w.get('ed'), w.get('et'))
