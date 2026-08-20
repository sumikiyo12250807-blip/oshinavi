# -*- coding: utf-8 -*-
"""7/3 built_0703.json(58件)を整形→50件。
- Music Fusion in Kyoto 音楽祭 3会場(1921木津川/1922京田辺/1923京丹後)→1エントリ(京都・3枠)
- 発売日(startDate)近い順で先頭50件を残す(発売前ファースト)・残りは今回見送り
出力: tmp/built_0703_final.json"""
import json, io, sys
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open('tmp/built_0703.json', encoding='utf-8'))
byid = {e['id']: e for e in d}

def label_date(iso):
    y, m, day = iso.split('-')
    return f"{y}年{int(m)}月{int(day)}日"

# --- Music Fusion 統合 (base=1921) ---
base = byid[1921]
members = [byid[1921], byid[1922], byid[1923]]
merged_ids = {1922, 1923}
tks = []
for m in members:
    t = dict(m['tickets'][0]); t['url'] = m['links']['pia']; tks.append(t)
tks.sort(key=lambda t: t['date'])          # 公演日昇順
perf = sorted(m['date'] for m in members)
venues = []
for m in members:
    if m['venue'] not in venues:
        venues.append(m['venue'])
base['name'] = "Music Fusion in Kyoto 音楽祭"
base['artist'] = "Music Fusion in Kyoto 音楽祭"
base['venue'] = "京都3会場（" + "／".join(venues) + "）"
base['prefecture'] = "京都"
base['date'] = perf[-1]
base['tickets'] = tks
base['dateLabel'] = f"{label_date(perf[0])}〜{label_date(perf[-1])} 京都3会場"

# --- 統合反映後リスト ---
work = [e for e in d if e['id'] not in merged_ids]

# --- 発売日(最早startDate)近い順で先頭50件 ---
def rls(e):
    starts = [t.get('startDate') for t in e.get('tickets', []) if t.get('startDate')]
    return min(starts) if starts else '9999-99-99'
work.sort(key=lambda e: (rls(e), e.get('date', '')))
KEEP = 50
final = work[:KEEP]
dropped = work[KEEP:]

json.dump(final, open('tmp/built_0703_final.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"最終 {len(final)}件 (58 - 統合{len(merged_ids)} - 見送り{len(dropped)})")
print("ジャンル下書き:", dict(Counter(e.get('_genre') for e in final)))
print("見送り(発売遅い順):", [(e['id'], rls(e), (e.get('name') or '')[:20]) for e in dropped])
print("=== 統合Music Fusion ===")
print("  venue=", base['venue'])
for t in base['tickets']:
    print("   -", t['type'])
