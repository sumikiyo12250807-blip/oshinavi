# -*- coding: utf-8 -*-
import json, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
res = json.load(open(r'C:\Users\user\oshinavi\tmp\_agentP2_result.json', encoding='utf-8'))

def norm(s):
    return re.sub(r'\s+', '', s)

fails = []
for r in res:
    if not r.get('ok'):
        print('FETCHFAIL', r['id'], r.get('err'))
        continue
    d = []
    if r['reg_count'] != r['buyable']:
        d.append(('枠数', r['reg_count'], f"{r['buyable']}(受付中{r['active']}/発売前{r['before']}/終了{r['ended']})"))
    if r['reg_date'] != r['maxdate_all']:
        d.append(('千秋楽', r['reg_date'], f"全枠max={r['maxdate_all']} 買える枠max={r['maxdate_buy']}"))
    regp = set(x for x in re.split(r'[・,]', r['reg_pref']) if x)
    pb = set(r['prefs_buy']); pa = set(r['prefs_all'])
    if regp != pb:
        d.append(('県', r['reg_pref'], f"買える枠={'・'.join(sorted(pb))} / 全枠={'・'.join(sorted(pa))}"))
    if d:
        fails.append((r, d))
    print('===', r['id'], r['reg_name'])
    print('   ぴあ名:', r['name'], '| ジャンル:', r['genre'], '| crumbs:', ' > '.join(r['crumbs']))
    print(f"   枠 登録{r['reg_count']} vs 実{r['buyable']} (受付中{r['active']}/発売前{r['before']}/終了{r['ended']})  日 登録{r['reg_date']} vs 実{r['maxdate_all']}(買{r['maxdate_buy']})  県 登録{r['reg_pref']} vs 買{'・'.join(sorted(pb))} 全{'・'.join(sorted(pa))}")
    for x in r['rows']:
        print(f"      [{x['state']}] {x['perfdate']}~{x['perf_end']} {x['pref']} {x['venue']} | {x['title']} | {x['statustext']} | {x['when']}")
print('\n--- ズレ件数:', len(fails))
