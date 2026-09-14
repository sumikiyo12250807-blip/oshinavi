# -*- coding: utf-8 -*-
"""X投稿の主役枠の候補について、明日9/13に発売が始まる枠を index.html から並べる（読むだけ・2026-09-12夜の便）。
主役の素材（shuyaku.md）に書く事実の土台＝ここに出た登録と、公式サイトで裏が取れたことだけ。
使い方: python tmp/x0914/main_cands.py
出力: tmp/x0914/main_cands.txt
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
DAY = '2026-09-14'
KEYS = ['新日本プロレス', '大相撲', '劇団四季', '木村拓哉', 'アンジュルム', '相川七瀬', 'ベイスターズ', 'SPY×FAMILY']
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
out = []
for k in KEYS:
    out.append('■ %s' % k)
    for e in ev:
        if e.get('genre') == 'new' or k not in ((e.get('artist') or '') + ' ' + (e.get('name') or '')):
            continue
        ts = [t for t in e.get('tickets') or [] if t.get('startDate') == DAY and not t.get('soldout')]
        if not ts:
            continue
        out.append('  id%s %s | %s | %s' % (e['id'], e.get('name'), e.get('dateLabel'), e.get('venue')))
        out.append('     売り場: pia=%s rakuten=%s eplus=%s' % ((e.get('links') or {}).get('pia'),
                   (e.get('links') or {}).get('rakuten'), (e.get('links') or {}).get('eplus')))
        for t in ts:
            out.append('     - %s | url=%s' % (t.get('type'), t.get('url') or '(カードのリンク)'))
io.open('tmp/x0914/main_cands.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('→ tmp/x0914/main_cands.txt (%d行)' % len(out))
