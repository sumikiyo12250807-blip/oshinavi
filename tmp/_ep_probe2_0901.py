# -*- coding: utf-8 -*-
import sys, re, html as H
sys.path.insert(0,'tools'); sys.stdout.reconfigure(encoding='utf-8')
from eplus_harvest import fetch
for u in ['https://eplus.jp/sf/detail/4531630001-P0030001P021001',
          'https://eplus.jp/sf/detail/4125060001-P0030013P021001']:
    h=fetch(u)
    print('===',u, len(h))
    txt = H.unescape(re.sub(r'<[^>]+>',' ', h))
    txt = re.sub(r'\s+',' ', txt)
    for kw in ['配信','アーカイブ','視聴','ライブ配信','見逃し']:
        for m in re.finditer(kw, txt):
            print(f'  [{kw}] ...{txt[max(0,m.start()-60):m.start()+60]}...')
            break
    # 券種名らしき箇所
    for m in re.finditer(r'(受付|発売)[^ ]{0,4}\s', txt):
        pass
    print('  TITLE:', (re.search(r'<title>(.*?)</title>', h, re.S) or [None,''])[1][:120])
