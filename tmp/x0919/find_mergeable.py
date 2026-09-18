# -*- coding: utf-8 -*-
"""同じ時刻・同じ県で、名前の末尾（vol.N／第N回／DAY1／昼夜／A公演など）だけが違う行を探す。

2026-09-18 ユーザー指摘＝
  「天皇杯…これまとめられるね」
  「ゴッデス…vol.1・vol.2でまとめて　そんな感じが他にもない確認して」

🚨探すだけ。畳むかどうかは1件ずつ見る（[[feedback_sports_home_away_never_merge]]＝
   応援する側が違う試合や、出演者が違う部は畳まない）。

  python tmp/x0919/find_mergeable.py
"""
import glob
import io
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

LINE = re.compile(r'^((?:\d{1,2}:\d{2})|時刻未定) (.+)／([^／]+?)(（先行）)?$')
# 名前の末尾につく「連番・回・部」の印
TAIL = re.compile(
    r'(?:\s*(?:vol\.?|Vol\.?|VOL\.?|ｖｏｌ\.?)\s*\d+'
    r'|\s*(?:DAY|Day|day)\s*\d+'
    r'|\s*第\s*\d+\s*(?:公演|部|回)'
    r'|\s*[（(]?\s*\d+\s*(?:部|公演)\s*[)）]?'
    r'|\s*[（(]?\s*(?:昼|夜|昼の部|夜の部|マチネ|ソワレ)\s*[)）]?'
    r'|\s*[ABC]\s*公演'
    r'|\s*[①-⑩]'
    r')+\s*$')

groups = defaultdict(list)
for f in sorted(glob.glob('tmp/x0919/post0*.txt')):
    for i, ln in enumerate(io.open(f, encoding='utf-8').read().split('\n'), 1):
        m = LINE.match(ln)
        if not m:
            continue
        t, name, pref, senko = m.group(1), m.group(2), m.group(3), m.group(4) or ''
        base = TAIL.sub('', name)
        if base != name:
            groups[(f, t, base, pref, senko)].append((i, name))

n = 0
for (f, t, base, pref, senko), rows in sorted(groups.items()):
    if len(rows) < 2:
        continue
    n += 1
    print('%s ｜%s %s／%s%s ← %d行' % (f[-10:], t, base, pref, senko, len(rows)))
    for i, name in rows:
        print('    %4d行 %s' % (i, name))
print('\nまとめられそうな組 %d' % n)
