# -*- coding: utf-8 -*-
"""発売前スイープの結果から、今日投入する候補を選ぶ。

選定ルール（memory）:
 - 発売前ファースト [[feedback_presale_first_harvest]]
 - **発売まで4日以上を最優先** [[feedback_harvest_countdown_first]]
 - 本日発売(TODAY)/発売日不明は投入しない（隠れ枠になる [[feedback_harvest_today_sale_enddate]]）
 - ジャンル優先順 ①音楽(J-POP最優先) ②演劇/ジャズ/クラシック/お笑い ③その他
   [[feedback_harvest_genre_priority]]（③を捨てるのではなくグループ内の並び）
 - 同名の既存エントリがあるものは**投入せず統合に回す** [[feedback_tour_consolidate]]
 - eventCd重複は落とす
"""
import json, io, sys, re, datetime, glob, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

TODAY = datetime.date.today()
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 100

# lg 番号 → 優先グループ
GROUP = {'01': 1, '02': 2, '07': 2, '03': 3, '04': 3, '05': 3, '06': 3}

rows, seen = [], set()
for p in sorted(glob.glob('tmp/sw03_*.json')):
    lg = re.search(r'sw03_(\d+)', p).group(1)
    d = json.load(io.open(p, encoding='utf-8'))
    for it in d['new']:
        cd = re.search(r'event(?:Bundle)?Cd=(\w+)', it['url'])
        cd = cd.group(1) if cd else it['url']
        if cd in seen:
            continue
        seen.add(cd)
        it['_lg'] = lg
        it['_grp'] = GROUP.get(lg, 3)
        it['_cd'] = cd
        rows.append(it)

print('スイープ全体の未掲載（eventCd重複除去後）: %d件' % len(rows))

def days_to_sale(it):
    m = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', it.get('rlsdate') or '')
    if not m:
        return None
    d = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return (d - TODAY).days

drop = {'本日発売/発売日不明': 0, '発売まで3日以内': 0, '同名の既存あり': 0}
cand = []
for it in rows:
    n = days_to_sale(it)
    if n is None:
        drop['本日発売/発売日不明'] += 1
        continue
    if n < 4:
        drop['発売まで3日以内'] += 1
        continue
    if it.get('name_in_db'):
        drop['同名の既存あり'] += 1
        continue
    it['_days'] = n
    cand.append(it)

print('除外:', ', '.join('%s %d' % kv for kv in drop.items()))
print('残り候補: %d件' % len(cand))

# ①グループ順 ②発売までが遠い順
cand.sort(key=lambda x: (x['_grp'], -x['_days']))
pick = cand[:LIMIT]

import collections
print('\n=== 投入候補 %d件 ===' % len(pick))
print('グループ内訳:', dict(collections.Counter(x['_grp'] for x in pick)))
print('lg内訳:', dict(collections.Counter(x['_lg'] for x in pick)))
print('発売までの日数: 最短%d日 / 最長%d日' % (
    min(x['_days'] for x in pick), max(x['_days'] for x in pick)))

json.dump(pick, open('tmp/pick_0825.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
# 統合に回す分（同名の既存あり）も残す
merge = [it for it in rows if it.get('name_in_db')]
json.dump(merge, open('tmp/merge_0825.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\nwritten tmp/pick_0825.json / 統合に回す %d件 → tmp/merge_0825.json' % len(merge))
