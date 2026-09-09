# -*- coding: utf-8 -*-
"""今日のバッチを選ぶ＝**発売前ファースト**＋足りない分を受付中の残りタネで埋める。

・発売前＝tmp/sweep_presale_0910/*.json（rlsStatus=0102 / 0202）
・受付中＝tmp/rest0101_0909.json（9/9のスイープで残した2,255件のタネ。スイープはやり直さない）
ジャンル優先順＝①音楽 ②演劇/クラシック ③その他（[[feedback_harvest_genre_priority]]）。
🚨締切が近いものも落とさない（2026-09-07 にユーザーが締切4日先の縛りを外した）。
🚨同名の既存があるものは投入せず統合行きに回す。

使い方: python tmp/pick_presale_0910.py [件数(既定100)]
"""
import collections
import glob
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

N = int(sys.argv[1]) if len(sys.argv) > 1 else 100
ORDER = ['01', '02', '07', '06', '03', '04', '05']
JP = {'01': '音楽', '02': '演劇', '07': 'クラシック', '06': 'イベント',
      '03': 'スポーツ', '04': '映画', '05': 'アート'}

# ① 発売前
by_lg = collections.defaultdict(dict)
for p in sorted(glob.glob('tmp/sweep_presale_0910/*.json')):
    mm = re.search(r'/(\d\d)_', p.replace('\\', '/'))
    if not mm:
        continue
    lg = mm.group(1)
    d = json.load(io.open(p, encoding='utf-8'))
    for c in d.get('new') or []:
        m = re.search(r'eventCd=(\w+)', c['url'])
        by_lg[lg].setdefault(m.group(1) if m else c['url'], c)

seen = set()
picked, hold = [], []
for lg in ORDER:
    for cd, c in by_lg[lg].items():
        if cd in seen:
            continue
        seen.add(cd)
        (hold if c.get('name_in_db') else picked).append((lg, cd, c, '発売前'))

print('【発売前】未掲載 %d件 ＝ 新規候補 %d / 統合行き %d' % (len(seen), len(picked), len(hold)))
print('  ジャンル内訳: %s' % dict(collections.Counter(JP[lg] for lg, _, _, _ in picked)))

# ② 足りなければ受付中の残りタネで埋める
rest = json.load(io.open('tmp/rest0101_0909.json', encoding='utf-8'))
rest_by_lg = collections.defaultdict(list)
for c in rest:
    if c['eventCd'] in seen:
        continue
    rest_by_lg[c['lg']].append(c)

fill = []
need = N - len(picked)
if need > 0:
    for lg in ORDER:
        for c in rest_by_lg[lg]:
            if len(fill) >= need:
                break
            if c['eventCd'] in seen:
                continue
            seen.add(c['eventCd'])
            fill.append((lg, c['eventCd'], {'artist': c['artist'], 'url': c['url']}, '受付中'))
        if len(fill) >= need:
            break
print('【受付中】残りタネ %d件から %d件を穴埋めに使う' % (len(rest), len(fill)))

batch = (picked + fill)[:N]
cnt = collections.Counter('%s/%s' % (JP[lg], src) for lg, _, _, src in batch)
print('\n今回のバッチ %d件（発売前 %d / 受付中 %d）'
      % (len(batch),
         sum(1 for b in batch if b[3] == '発売前'),
         sum(1 for b in batch if b[3] == '受付中')))
for k, v in cnt.most_common():
    print('   %-14s %d件' % (k, v))

json.dump([{'artist': c['artist'], 'urls': [c['url']], 'eventCd': cd}
           for lg, cd, c, s in batch],
          io.open('tmp/cand_0910.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump([{'eventCd': cd, 'artist': c['artist'], 'url': c['url'], 'lg': lg}
           for lg, cd, c, s in hold],
          io.open('tmp/merge_0910.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
left = [x for x in rest if x['eventCd'] not in {b[1] for b in batch}]
json.dump(left, io.open('tmp/rest0101_0910.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\n→ tmp/cand_0910.json（今回）/ tmp/merge_0910.json（統合行き %d件）/ '
      'tmp/rest0101_0910.json（受付中の残り %d件）' % (len(hold), len(left)))
