# -*- coding: utf-8 -*-
"""明日(8/30 日)に差し替える号の素材。対象＝2026-08-31(月)〜09-06(日) に発売が始まる枠。
主役は件数でなくアーティスト名（feedback: 記事の主役はアーティスト名）。
・スポーツの席種違いは「同じ公演」に潰す（阪神の券種12種で上位を埋めない）
・深掘り候補＝最終公演日が当分先のもの（すぐ終わるツアーは1週間で消える）
"""
import io, re, json, sys, collections

sys.stdout.reconfigure(encoding='utf-8')
FROM, TO = '2026-08-31', '2026-09-06'

h = io.open('index.html', encoding='utf-8', newline='').read()
E = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))

by = collections.defaultdict(lambda: {
    'slots': 0, 'ev': set(), 'genre': None, 'last': '', 'first': '',
    'days': set(), 'prefs': set(), 'shows': set(), 'url': ''})

for e in E:
    hit = []
    for t in (e.get('tickets') or []):
        if t.get('soldout') or t.get('saleEnded'):
            continue
        sd = t.get('startDate') or ''
        if not (FROM <= sd <= TO):
            continue
        ty = t.get('type') or ''
        if not re.search(r'\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2}発売', ty):
            continue
        hit.append(t)
    if not hit:
        continue
    a = e.get('artist') or e.get('name') or ''
    v = by[a]
    v['ev'].add(e['id'])
    v['genre'] = e.get('genre')
    v['last'] = max(v['last'], e.get('date') or '')
    v['url'] = v['url'] or (e.get('links') or {}).get('pia') or ''
    for p in re.split(r'[・／/]', e.get('prefecture') or ''):
        if p.strip():
            v['prefs'].add(p.strip())
    for t in hit:
        v['days'].add(t['startDate'])
        v['first'] = min(v['first'] or '9999', t['startDate'])
        # 券種違いを潰す＝「（県 M/D公演）」の中身で公演を数える
        m = re.search(r'（([^）]*?公演)）', t.get('type') or '')
        v['shows'].add(m.group(1) if m else (t.get('type') or ''))
        v['slots'] += 1

rows = sorted(by.items(), key=lambda kv: (-len(kv[1]['shows']), -kv[1]['slots'], kv[0]))

o = io.open('tmp/weekly_material_0830.md', 'w', encoding='utf-8')
o.write('# 8/31(月)〜9/6(日) に発売が始まるアーティスト %d組\n\n' % len(rows))
o.write('「公演」＝券種違いを潰した実公演数／「枠」＝販売枠の数／「最終公演日」＝深掘り向きの目安\n\n')
o.write('| # | アーティスト／公演 | ジャンル | 公演 | 枠 | 県 | 発売開始 | 最終公演日 |\n')
o.write('|---|---|---|---|---|---|---|---|\n')
for i, (a, v) in enumerate(rows[:70], 1):
    o.write('| %d | %s | %s | %d | %d | %s | %s | %s |\n' % (
        i, a.replace('|', '｜')[:46], v['genre'], len(v['shows']), v['slots'],
        '・'.join(sorted(v['prefs']))[:22], v['first'][5:], v['last']))
o.close()
print('組数 %d → tmp/weekly_material_0830.md' % len(rows))
print('上位15組:')
for a, v in rows[:15]:
    print('  %2d公演 %2d枠 [%-8s] 発売%s 最終%s  %s' % (
        len(v['shows']), v['slots'], v['genre'], v['first'][5:], v['last'], a[:40]))
