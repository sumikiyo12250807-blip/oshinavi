# -*- coding: utf-8 -*-
"""genre=="new" のプールを一覧する（id / _genre下書き / 公演名 / 会場 / 公演日 / ぴあURL）"""
import io, json, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

raw = io.open('index.html', 'r', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n', raw, re.S).group(1))
pool = [e for e in EVENTS if e.get('genre') == 'new']

cnt = collections.Counter(e.get('_genre') or '(空)' for e in pool)
print('=== 新着プール %d件 / _genre下書きの内訳 ===' % len(pool))
for g, n in cnt.most_common():
    print('   %-12s %d' % (g, n))
print()
for e in pool:
    links = e.get('links') or {}
    url = links.get('pia') or links.get('eplus') or links.get('rakuten') or links.get('lawson') or ''
    print('id%-5s %-10s %-34s %-22s %s' % (
        e['id'], e.get('_genre') or '(空)', (e.get('artist') or '')[:32],
        (e.get('venue') or '')[:20], e.get('date') or ''))
    print('       %s' % url)
