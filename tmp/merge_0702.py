# -*- coding: utf-8 -*-
"""built_0702.json(58件)を同一公演統合＋期限切迫除外で50件に整える。
- 多都市同一公演→全国ツアー形(各ticketにcity別url・venue列挙・pref全国)
- 同一劇場の連続興行(吉本)→1エントリ複数ticket(venue据置)
出力: tmp/built_0702_final.json"""
import json, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open('tmp/built_0702.json', encoding='utf-8'))
byid = {e['id']: e for e in d}

def mmdd(iso):
    y, m, day = iso.split('-')
    return int(m), int(day)
def label_date(iso):
    y, m, day = iso.split('-')
    return f"{y}年{int(m)}月{int(day)}日"

# 統合グループ: keep, adds, 表示名, mode('tour'=多都市全国ツアー / 'venue'=同一劇場連続)
GROUPS = [
    (1821, [1822], "五十嵐紅|ギターと静寂 特別公演『星と祈り』", 'tour'),
    (1824, [1825], "五十嵐紅トリオ|ジブリ 2026【A】", 'tour'),
    (1865, [1866], "第30回英国歌曲展Plus 辻裕久テノールリサイタル", 'tour'),
    (1860, [1861, 1862], "第17回 音楽大学オーケストラ・フェスティバル 2026", 'tour'),
    (1853, [1854, 1855], "吉本新喜劇inセカンドシアター", 'venue'),
]
DROP = [1814]  # 響-祈りの四季-: 一般発売が本日7/2 23:59締切+翌7/3当日券のみ=発売前ではなく期限切迫

merged_ids = set()
for keep, adds, name, mode in GROUPS:
    base = byid[keep]
    members = [base] + [byid[i] for i in adds]
    merged_ids.update(adds)
    # ticket集約(各memberの先頭ticketにurl付与)
    tks = []
    for m in members:
        t = dict(m['tickets'][0])
        t['url'] = m['links']['pia']
        tks.append(t)
    perf = sorted(m['date'] for m in members)
    base['artist'] = name
    base['name'] = name
    base['date'] = perf[-1]
    base['tickets'] = tks
    if mode == 'tour':
        venues = []
        for m in members:
            if m['venue'] not in venues:
                venues.append(m['venue'])
        base['venue'] = "全国ツアー（" + "／".join(venues) + "）"
        base['prefecture'] = "全国"
        if perf[0] == perf[-1]:
            base['dateLabel'] = f"{label_date(perf[0])} 全国ツアー"
        else:
            base['dateLabel'] = f"{label_date(perf[0])}〜{label_date(perf[-1])} 全国ツアー"
        base['links']['pia'] = members[0]['links']['pia']
    else:  # venue: 同一劇場連続興行
        base['dateLabel'] = f"{label_date(perf[0])}〜{label_date(perf[-1])} {base['prefecture']} {base['venue']}"

# 最終リスト構築(元順序維持・統合されたaddとDROPを除外)
final = [e for e in d if e['id'] not in merged_ids and e['id'] not in DROP]
json.dump(final, open('tmp/built_0702_final.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"最終 {len(final)}件 (58 - 統合{len(merged_ids)} - 除外{len(DROP)})")
from collections import Counter
print("ジャンル下書き:", dict(Counter(e['_genre'] for e in final)))
for e in final:
    if len(e['tickets']) > 1 or e['id'] in [g[0] for g in GROUPS]:
        tb = ' | '.join(f"{t['type']}" for t in e['tickets'])
        print(f"  ★統合 {e['id']} {e['name'][:34]} [{e['prefecture']}] {e['venue'][:40]}")
