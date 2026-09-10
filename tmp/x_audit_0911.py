# -*- coding: utf-8 -*-
"""X投稿に出す3組を、ぴあでアーティスト名から総ざらいして取りこぼしを潰す。

夜の便の決まり（.claude/skills/day/SKILL.md 第4便 8番）＝
「予約した投稿に出てくる公演を、OSHINAVI側で総ざらいして取りこぼしを潰してからpush」
理由＝X投稿の誘導先は oshinavi.jp。着地したページに公演が欠けていたら、
わざわざ来た人が自分の推しを見つけられない。

🚨ツアーまとめ(bundle)だけ見ない＝そこに出てこない公演がある
（[[feedback_pia_bundle_hides_shows]]）。だからアーティスト名で引く。
"""
import io
import json
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

NAMES = ['なとり', '野村萬斎', '春風亭昇太']

h = io.open('index.html', encoding='utf-8').read()
codes = set(re.findall(r'event(?:Bundle)?Cd=([\w]+)', h))

out = {}
for nm in NAMES:
    subprocess.run([sys.executable, 'tools/pia_kw_search.py', nm],
                   capture_output=True, timeout=300)
    txt = io.open('tmp/pia_kw_search.txt', encoding='utf-8').read()
    hits = []
    for blk in re.findall(
            r'\n\[(.*?)\] (.*?)\n\s+公演日: (.*?)\n\s+会場  : (.*?)\n(?:\s+発売日: (.*?)\n)?\s+URL   : (\S+)',
            txt):
        cd = (re.search(r'event(?:Bundle)?Cd=([\w]+)', blk[5]) or [None, ''])[1]
        hits.append({'state': blk[0], 'name': blk[1], 'date': blk[2], 'venue': blk[3],
                     'sale': blk[4], 'url': blk[5], 'registered': cd in codes})
    out[nm] = hits
    miss = [x for x in hits if not x['registered']]
    print('== %s : ぴあ %d件 / うち未登録 %d件' % (nm, len(hits), len(miss)))
    for x in miss:
        print('   **未登録** [%s] %-40s %s / %s' % (x['state'], x['name'][:40],
                                                x['date'][:24], x['venue'][:22]))
        print('        %s%s' % (x['url'], ('  発売 ' + x['sale']) if x['sale'] else ''))
    time.sleep(1.2)

json.dump(out, io.open('tmp/x_audit_0911.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('')
print('-> tmp/x_audit_0911.json')
