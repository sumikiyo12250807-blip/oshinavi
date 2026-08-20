# -*- coding: utf-8 -*-
"""楽天：新着候補を更新日で絞る＋既存DBの楽天エントリ数を数える。"""
import sys, re, json, collections
sys.stdout.reconfigure(encoding='utf-8')

rows = json.load(open('tmp/rakuten_new_urls.json', encoding='utf-8'))
cnt = collections.Counter(r['lastmod'][:7] for r in rows)
print('=== 更新日(lastmod)の分布・新しい順 ===')
for k in sorted(cnt, reverse=True)[:14]:
    print('  %s  %5d件' % (k, cnt[k]))

recent = [r for r in rows if r['lastmod'][:7] >= '2026-07']
print('\n2026-07以降の更新:', len(recent), '件')
json.dump(recent, open('tmp/rakuten_recent.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))
rk = [e for e in EV if 'rakuten' in json.dumps(e.get('links') or {}, ensure_ascii=False)]
print('既存DBで楽天リンクを持つエントリ:', len(rk), '件')

print('\n=== 2026-07更新の楽天URL（先頭30）===')
for r in recent[:30]:
    print('  %s %s' % (r['lastmod'][:10], r['url']))
