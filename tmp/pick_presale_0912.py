# -*- coding: utf-8 -*-
"""今朝の発売前スイープ（tmp/sweep_presale_0912/*.json の new＝eventCd が未登録の行）から候補を選ぶ（読むだけ）。
9/11版から変えたところ＝受付中の穴埋めはしない（受付中は tmp/cand_uk_0912.json に100件を別に選んである）。
・ジャンル優先順＝①音楽 ②演劇/クラシック ③その他（[[feedback_harvest_genre_priority]]）
・🚨締切が近いものも落とさない（2026-09-07 ユーザー決定）
・🚨同名の既存があるもの（name_in_db）は投入せず統合行きに回す
使い方: python tmp/pick_presale_0912.py
出力: tmp/cand_0912.json（新規候補）／ tmp/merge_0912.json（統合行き）
"""
import collections
import glob
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
ORDER = ['01', '02', '07', '06', '03', '04', '05']
JP = {'01': '音楽', '02': '演劇', '07': 'クラシック', '06': 'イベント',
      '03': 'スポーツ', '04': '映画', '05': 'アート'}

by_lg = collections.defaultdict(dict)
pages = []
for p in sorted(glob.glob('tmp/sweep_presale_0912/*.json')):
    mm = re.search(r'/(\d\d)_', p.replace('\\', '/'))
    if not mm:
        continue
    lg = mm.group(1)
    d = json.load(io.open(p, encoding='utf-8'))
    pages.append('%s total=%s pages=%s fetched=%s' % (p.split('/')[-1].split('\\')[-1],
                                                     d.get('total'), d.get('pages'), d.get('fetched_pages')))
    for c in d.get('new') or []:
        m = re.search(r'eventCd=(\w+)', c['url'])
        by_lg[lg].setdefault(m.group(1) if m else c['url'], c)

print('【ページ到達】')
for s in pages:
    print('   ' + s)
seen, picked, hold, today = set(), [], [], []
for lg in ORDER:
    for cd, c in by_lg[lg].items():
        if cd in seen:
            continue
        seen.add(cd)
        if c.get('rlsdate') == 'TODAY':
            today.append((lg, cd, c))      # 本日発売＝隠れ枠になる（昼のヒールの受け持ち）が、候補からは落とさず数える
        (hold if c.get('name_in_db') else picked).append((lg, cd, c))
print('【発売前】未掲載 %d件 ＝ 新規候補 %d / 統合行き %d（うち本日発売 %d）'
      % (len(seen), len(picked), len(hold), len(today)))
print('  新規のジャンル内訳: %s' % dict(collections.Counter(JP[lg] for lg, _, _ in picked)))
json.dump([{'artist': c['artist'], 'urls': [c['url']], 'eventCd': cd, 'lg': lg, 'rlsdate': c.get('rlsdate')}
           for lg, cd, c in picked],
          io.open('tmp/cand_0912.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump([{'eventCd': cd, 'artist': c['artist'], 'url': c['url'], 'lg': lg, 'rlsdate': c.get('rlsdate')}
           for lg, cd, c in hold],
          io.open('tmp/merge_0912.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('→ tmp/cand_0912.json（新規 %d）／ tmp/merge_0912.json（統合行き %d）' % (len(picked), len(hold)))
