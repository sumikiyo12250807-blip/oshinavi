# -*- coding: utf-8 -*-
"""ヒール本体（tmp/heal_stale.json）の convert のうち、実際には当たらなかった＝安全弁で止まった id を出す（読むだけ）。
heal の出力を途中で切って読み損ねた時の出し直し用。いまの index.html の枠の券種名が、取り直しの券種名を
1本も含んでいなければ「当たっていない」とみなす。
使い方: python tmp/heal_blocked_0914.py
出力: tmp/heal_blocked_0914.txt
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
heal = [h for h in json.load(io.open('tmp/heal_stale.json', encoding='utf-8')) if h.get('status') == 'convert']
src = io.open('index.html', encoding='utf-8').read()
by = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
applied, blocked, gone = [], [], []
for h in heal:
    e = by.get(h['id'])
    if not e:
        gone.append(h['id'])
        continue
    now = {t.get('type') for t in e.get('tickets') or []}
    new = {t.get('type') for t in h.get('tickets') or []}
    (applied if new <= now else blocked).append(h)
out = ['convert %d件 ＝ 当たった %d件 / 当たっていない %d件 / エントリが無い %d件 %s' % (
    len(heal), len(applied), len(blocked), len(gone), gone)]
for h in blocked:
    e = by[h['id']]
    now = [t.get('type') for t in e.get('tickets') or []]
    new = [t.get('type') for t in h.get('tickets') or []]
    out.append('== id%s %s' % (h['id'], (e.get('name') or '')[:40]))
    out.append('   いま: %s' % ' ／ '.join(now[:6]) + (' ほか%d' % (len(now) - 6) if len(now) > 6 else ''))
    out.append('   取り直し: %s' % ' ／ '.join(new[:6]) + (' ほか%d' % (len(new) - 6) if len(new) > 6 else ''))
io.open('tmp/heal_blocked_0914.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(out[0])
print('→ tmp/heal_blocked_0914.txt')
