# -*- coding: utf-8 -*-
"""今朝のぴあ発売前スイープ（rlsStatus=0102＋0202・全7ジャンル）の候補を集約して仕分ける。
  ①URL重複を落とす ②同名の既存あり＝統合行き ③本日発売/日付不明＝除外 ④本当に新規＝投入候補
"""
import glob
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

merged, seen = [], set()
for p in sorted(glob.glob('tmp/_sw_*_0901.json')):
    d = json.load(open(p, encoding='utf-8'))
    for it in d.get('new', []):
        if it['url'] in seen:
            continue
        seen.add(it['url'])
        it['_lg'] = d['lg']
        merged.append(it)

samename = [x for x in merged if x.get('name_in_db')]
rest = [x for x in merged if not x.get('name_in_db')]
today = [x for x in rest if x.get('rlsdate') == 'TODAY']
nodate = [x for x in rest if not x.get('rlsdate')]
fresh = [x for x in rest if x.get('rlsdate') and x['rlsdate'] != 'TODAY']

print(f'スイープ候補（URL重複除去後） {len(merged)}件')
print(f'  同名の既存あり（統合行き）      {len(samename)}件')
print(f'  本日発売（隠れ枠になるので除外） {len(today)}件')
print(f'  発売日が取れない（保留）        {len(nodate)}件')
print(f'  本当に新規（投入候補）          {len(fresh)}件')
by = {}
for x in fresh:
    by[x['_lg']] = by.get(x['_lg'], 0) + 1
LG = {'01': '音楽', '02': '演劇', '03': 'スポーツ', '04': '映画', '05': 'アート', '06': 'イベント', '07': 'クラシック'}
print('  内訳: ' + ' / '.join(f'{LG.get(k, k)} {v}' for k, v in sorted(by.items())))

json.dump(fresh, open('tmp/_newfresh_0901.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(samename, open('tmp/_newsame_0901.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('→ tmp/_newfresh_0901.json / tmp/_newsame_0901.json')
