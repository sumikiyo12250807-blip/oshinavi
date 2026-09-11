# -*- coding: utf-8 -*-
"""受付中（rlsStatus=0101）の残りタネから今日のバッチを選ぶ（2026-09-12）。
・タネ＝tmp/rest0101_0911.json（9/9の総ざらいの残り）
・🚨タネは2日前のものなので、いま index.html に同じ eventCd があるものは外す（統合や救済で入った分）
・ジャンル優先順＝①音楽 ②演劇/クラシック ③その他（[[feedback_harvest_genre_priority]]）
・締切が近くても落とさない（2026-09-07 ユーザー決定）
・同名の既存があるものは統合行きに回す（name_in_db の判定は投入前の dedup で再確認する）
使い方: python tmp/pick_uketsuke_0911.py [件数=100]
出力: tmp/cand_uk_0912.json ／ tmp/rest0101_0911b.json（残り）
"""
import collections, io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
N = int(sys.argv[1]) if len(sys.argv) > 1 else 100
ORDER = ['01', '02', '07', '06', '03', '04', '05']
rest = json.load(io.open('tmp/rest0101_0911c.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
have = set(re.findall(r'eventCd=(\d+)', h))
by = collections.defaultdict(list)
gone = 0
for c in rest:
    if c['eventCd'] in have:
        gone += 1
        continue
    by[c['lg']].append(c)
pick = []
for lg in ORDER:
    for c in by[lg]:
        if len(pick) >= N:
            break
        pick.append(c)
left = [c for c in rest if c not in pick and c['eventCd'] not in have]
print('タネ %d件 ／ もう登録済みで外した %d件 ／ 選んだ %d件 ／ 残り %d件' % (len(rest), gone, len(pick), len(left)))
print('  内訳: %s' % dict(collections.Counter(c['lg'] for c in pick)))
json.dump([{'artist': c['artist'], 'urls': [c['url']], 'eventCd': c['eventCd']} for c in pick],
          io.open('tmp/cand_uk_0912.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(left, io.open('tmp/rest0101_0912.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
