# -*- coding: utf-8 -*-
"""ローチケにあってOSHINAVIに無い7件を、ぴあで当たる。

ぴあに在れば「ぴあの取りこぼし」＝拾う。
ぴあに無ければ「ローチケ独占」＝ローチケから拾う（実ブラウザ）。
"""
import io
import json
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

NAMES = ['w.o.d.', '中西圭三', '澤田知可子', 'THE MADNA', 'REVERSE EDGE',
         '橘いずみ', '野田かつひこ', '別府葉子']

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
    for x in hits[:4]:
        print('   %s [%s] %-38s %s / %s' % ('✅登録済' if x['registered'] else '🚨未登録',
                                            x['state'], x['name'][:38], x['date'][:20], x['venue'][:20]))
        if not x['registered']:
            print('        %s%s' % (x['url'], ('  発売 ' + x['sale']) if x['sale'] else ''))
    time.sleep(0.8)

json.dump(out, io.open('tmp/hunt_lt7_0910.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\n→ tmp/hunt_lt7_0910.json')
