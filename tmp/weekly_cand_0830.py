# -*- coding: utf-8 -*-
"""来週号「今週のピックアップ」の候補を絞る。
主役は件数でなく**アーティスト名**（feedback: 記事の主役はアーティスト名）。
・スポーツの席種違いは1枠に潰す（阪神の券種12種で上位を埋めない）
・深掘り候補＝公演が当分先まで続くもの（すぐ終わるツアーは1週間で消える）"""
import io, re, json, sys, collections, datetime
sys.stdout.reconfigure(encoding='utf-8')
FROM, TO = '2026-08-31', '2026-09-06'
h = io.open('index.html', encoding='utf-8', newline='').read()
E = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))

rows = []
for e in E:
    hit = []
    for t in (e.get('tickets') or []):
        if t.get('soldout') or t.get('saleEnded'):
            continue
        sd = t.get('startDate') or ''
        if not (FROM <= sd <= TO):
            continue
        if not re.search(r'\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2}発売', t.get('type') or ''):
            continue
        hit.append(t)
    if hit:
        rows.append((e, hit))

by = collections.defaultdict(lambda: {'days': set(), 'ev': set(), 'genre': None, 'last': '', 'name': ''})
for e, hit in rows:
    a = e.get('artist') or e.get('name')
    v = by[a]
    v['ev'].add(e['id']); v['genre'] = e.get('genre'); v['name'] = a
    v['last'] = max(v['last'], e.get('date') or '')
    for t in hit:
        v['days'].add(t['startDate'])

o = io.open('tmp/weekly_cand_0830.txt', 'w', encoding='utf-8')
o.write('=== 来週(8/31〜9/6)に発売が始まるアーティスト %d組 ===\n' % len(by))
o.write('（席種違いは潰して「発売日の数」で並べた。last=そのアーティストの最終公演日＝深掘り向きの目安）\n\n')
for a, v in sorted(by.items(), key=lambda kv: (-len(kv[1]['days']), -len(kv[1]['ev']), kv[0])):
    o.write('%-2d日 ev%-2d [%-9s] last=%s  %s\n' % (
        len(v['days']), len(v['ev']), v['genre'], v['last'], a))
o.close()
print('組数', len(by))
