# -*- coding: utf-8 -*-
"""隠れ枠（startDate==date<=今日・売り切れまで販売でない）の数を、今夜の手当ての前後で比べる（2026-09-14 夜）。
check_order.js が「隠れ枠47枠」と出した。今夜の足し算（heal_blocked_union_1805.py）は元の枠を残すので、
あたしが増やしたのか、前からあったのかを数える。
使い方: python tmp/stale_count_compare_0914.py
"""
import json
import re
import subprocess
import sys

sys.path.insert(0, 'tools')
import heal_stale_deadlines as H

sys.stdout.reconfigure(encoding='utf-8')


def stale_of(text):
    ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', text, re.S).group(1))
    out = {}
    for e in ev:
        n = sum(1 for t in e.get('tickets') or [] if H.is_stale(t) and not t.get('soldout'))
        if n:
            out[e['id']] = n
    return out


def at(rev):
    return subprocess.run(['git', 'show', '%s:index.html' % rev], capture_output=True).stdout.decode('utf-8')


before = stale_of(at('a78e8ce5'))
head = stale_of(at('HEAD'))
now = stale_of(open('index.html', encoding='utf-8').read())
for lab, d in [('今夜の手当ての前 a78e8ce5', before), ('HEAD', head), ('現物', now)]:
    print('%s ＝ %d枠（%d件）' % (lab, sum(d.values()), len(d)))
up = {i: (before.get(i, 0), n) for i, n in now.items() if n > before.get(i, 0)}
print('\n手当ての前より増えたエントリ %d件' % len(up))
for i, (a, b) in sorted(up.items()):
    print('  id%-5s %d→%d' % (i, a, b))
