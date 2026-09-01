# -*- coding: utf-8 -*-
import sys, re, html as H
sys.path.insert(0,'tools'); sys.stdout.reconfigure(encoding='utf-8')
from eplus_harvest import fetch, parse_ld, parse_windows
for u in ['https://eplus.jp/sf/detail/0743570001-P0030010P021001',
          'https://eplus.jp/sf/detail/0743570001-P0030010P021003',
          'https://eplus.jp/sf/detail/4536580001-P0030002P021001',
          'https://eplus.jp/sf/detail/4572850001-P0030002P021002',
          'https://eplus.jp/sf/detail/4572040001-P0030001P021001',
          'https://eplus.jp/sf/detail/0025220003-P0030073P021001']:
    h=fetch(u); print('===',u)
    for e in parse_ld(h): print('   公演', e.get('date'), e.get('time'), '|', e.get('venue'), '|', (e.get('name') or '')[:50])
    ws=parse_windows(h)
    print('   窓', len(ws))
    for w in ws: print('     ', w.get('kind'),'|',w.get('label'),'| sd',w.get('sd'),w.get('st'),'| ed',w.get('ed'),w.get('et'),'| st?',w.get('status'))
    txt=re.sub(r'\s+',' ', H.unescape(re.sub(r'<[^>]+>',' ',h)))
    for kw in ['予定枚数','受付終了','販売終了','完売']:
        if kw in txt:
            i=txt.find(kw); print(f'   [{kw}] ...{txt[max(0,i-70):i+70]}...')
