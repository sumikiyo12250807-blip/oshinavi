# -*- coding: utf-8 -*-
"""ローチケ 9/21-9/27発売で「載っていない」6件を、ぴあで当たる。

ぴあに在れば「ぴあの取りこぼし」＝ぴあから拾う（後工程が揃っているので確実）。
ぴあに無ければ「ローチケ独占」＝ローチケから拾う（実ブラウザ）。
"""
import io
import json
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

NAMES = ['櫻坂46', '歌声コンサート', '長崎スタジアムシティ', '星波',
         '東京キューバンボーイズ', '岩崎宏美']

h = io.open('index.html', encoding='utf-8').read()
codes = set(re.findall(r'event(?:Bundle)?Cd=([\w]+)', h))

out = {}
for nm in NAMES:
    subprocess.run([sys.executable, 'tools/pia_kw_search.py', nm],
                   capture_output=True, timeout=300)
    txt = io.open('tmp/pia_kw_search.txt', encoding='utf-8').read()
    hits = []
    for blk in re.findall(r'\n\[(.*?)\] (.*?)\n\s+公演日: (.*?)\n\s+会場  : (.*?)\n(?:\s+発売日: (.*?)\n)?\s+URL   : (\S+)', txt):
        cd = (re.search(r'event(?:Bundle)?Cd=([\w]+)', blk[5]) or [None, ''])[1]
        hits.append({'state': blk[0], 'name': blk[1], 'date': blk[2], 'venue': blk[3],
                     'sale': blk[4], 'url': blk[5], 'registered': cd in codes})
    out[nm] = hits
    print('== %s ぴあ %d件' % (nm, len(hits)))
    for x in hits[:6]:
        print('   %s [%s] %-34s %s / %s' % ('OK-登録済' if x['registered'] else '**未登録**',
                                            x['state'], x['name'][:34], x['date'][:20], x['venue'][:18]))
        if not x['registered']:
            print('        %s%s' % (x['url'], ('  発売 ' + x['sale']) if x['sale'] else ''))
    time.sleep(1.2)

json.dump(out, io.open('tmp/hunt_lt6_0910.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\n-> tmp/hunt_lt6_0910.json')
