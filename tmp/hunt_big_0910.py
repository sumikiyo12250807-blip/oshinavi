# -*- coding: utf-8 -*-
"""載っていない大物21件を、ぴあで総ざらいして「本当に無いのか」を確かめる。

🚨「載っていない」には3つの理由がある。区別してから動く:
  ① 本当に取りこぼし（拾いに行く）
  ② その売り場の独占で、ぴあ・楽天に無い（そこから拾う）
  ③ ファンクラブ先行だけで一般発売がまだ（載せる枠がまだ無い）
"""
import io
import json
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

NAMES = ['=LOVE', 'CHEMISTRY', 'ファンキーモンキーベイビーズ', '細野晴臣', 'RUNIDRE',
         'REBECCA', 'KENTO YAMAZAKI', 'DOES', 'KO1KEYZ', 'チルクラシック',
         'King Gnu', 'Da-iCE', 'BE:FIRST', "ONE N' ONLY", 'ILLIT',
         'BMSG', '竜とそばかすの姫', 'MTV VMAJ', 'ザ・フェイク', '京まふ', 'XMF']

out = {}
for nm in NAMES:
    r = subprocess.run([sys.executable, 'tools/pia_kw_search.py', nm],
                       capture_output=True, timeout=300)
    try:
        txt = io.open('tmp/pia_kw_search.txt', encoding='utf-8').read()
    except Exception:
        txt = ''
    m = re.search(r'=== ヒット (\d+) 件', txt)
    n = int(m.group(1)) if m else 0
    hits = []
    for blk in re.findall(r'\n\[(.*?)\] (.*?)\n\s+公演日: (.*?)\n\s+会場  : (.*?)\n(?:\s+発売日: (.*?)\n)?\s+URL   : (\S+)', txt):
        hits.append({'state': blk[0], 'name': blk[1], 'date': blk[2],
                     'venue': blk[3], 'sale': blk[4], 'url': blk[5]})
    out[nm] = {'count': n, 'hits': hits}
    print('%-26s ぴあ %d件' % (nm[:26], n))
    for x in hits[:5]:
        print('     [%s] %-40s %s / %s%s' % (x['state'], x['name'][:40], x['date'][:24],
                                             x['venue'][:24],
                                             ('  発売 ' + x['sale']) if x['sale'] else ''))
        print('        %s' % x['url'])
    time.sleep(1.0)

json.dump(out, io.open('tmp/hunt_big_0910.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\n→ tmp/hunt_big_0910.json')
