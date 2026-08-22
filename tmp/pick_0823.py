# -*- coding: utf-8 -*-
"""8/23 朝の新着選定。
方針（PLAYBOOK）:
  - 発売前ファースト（rlsIn=03 のみ使う）
  - 発売まで4日以上を最優先 / 本日発売(TODAY)は隠れ枠になるので除外
  - ジャンル優先順 ①音楽(01) ②演劇(02)・クラシック(07) ③その他(03/04/05/06)
  - 同名の既存エントリがあるもの(name_in_db)は投入せず「統合に回す」へ分ける
"""
import io, json, datetime, collections

TODAY = datetime.date.today()
GENRE_ORDER = ['01', '02', '07', '06', '03', '04', '05']
LIMIT = 100

def parse_rls(s):
    try:
        y, m, d = s.split('/')
        return datetime.date(int(y), int(m), int(d))
    except Exception:
        return None

pick, merge, skip = [], [], []
for g in GENRE_ORDER:
    try:
        d = json.load(io.open('tmp/presale_%s_0823.json' % g, encoding='utf-8'))
    except IOError:
        continue
    for it in d['new']:
        it['lg'] = g
        rd = parse_rls(it.get('rlsdate') or '')
        it['_days'] = (rd - TODAY).days if rd else None
        if it.get('name_in_db'):
            merge.append(it)
        elif it['_days'] is None:
            skip.append(it)
        elif it['_days'] <= 0:
            skip.append(it)          # 本日発売＝隠れ枠になるので投入しない
        else:
            pick.append(it)

# 発売まで4日以上を最優先 → ジャンル優先順 → 発売日が近い順
def key(it):
    far = 0 if it['_days'] >= 4 else 1
    return (far, GENRE_ORDER.index(it['lg']), it['_days'])

pick.sort(key=key)
chosen = pick[:LIMIT]

cnt = collections.Counter(it['lg'] for it in chosen)
far = sum(1 for it in chosen if it['_days'] >= 4)
print('候補total=%d / 同名既存(統合へ)=%d / 除外(本日発売・日付不明)=%d' % (len(pick), len(merge), len(skip)))
print('選定=%d  内訳 %s  発売まで4日以上=%d/%d' % (len(chosen), dict(cnt), far, len(chosen)))
json.dump(chosen, io.open('tmp/pick_0823.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(merge, io.open('tmp/merge_cand_0823.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(skip, io.open('tmp/skip_0823.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

o = io.open('tmp/pick_0823.txt', 'w', encoding='utf-8')
for it in chosen:
    o.write('%s | 発売%s(あと%d日) | %s | %s | %s\n' % (
        it['lg'], it['rlsdate'], it['_days'], it['artist'], it['perfdate'], it['url']))
o.close()
print('→ tmp/pick_0823.json / tmp/pick_0823.txt')
