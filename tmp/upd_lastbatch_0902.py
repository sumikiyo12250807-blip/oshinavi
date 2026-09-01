# -*- coding: utf-8 -*-
"""last_batch.json に今朝の投入を記録する（翌朝の再チェックの入力になる）。"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
P = '.claude/state/last_batch.json'
d = json.load(open(P, encoding='utf-8'))
d['batches'].append({
    'date': '2026-09-02',
    'slot': 'morning',
    'id_from': 6270,
    'id_to': 6356,
    'count': 70,
    'source': 'ぴあ 発売前 rlsStatus=0102(先着)＋0202(抽選) を7ジャンル総ざらい',
    'assigned': False,
    'rechecked': False,
    'note': ('今日の流入＝未掲載174件（URL重複除去後）。内訳＝同名既存71（統合行き・未処理）／'
             '本日発売12（隠れ枠になるので除外）／発売日が取れない4（保留）／本当に新規87。'
             '87件をビルドして全件成立(skip 0・114枠)。'
             '🚨緩い部分一致で既存とぶつかった17件は投入せず保留し、別エージェントに'
             '「同じツアーか別物か」を実ページで調べさせた（tmp/hold_ids_0902.txt）。'
             '残り70件（91枠）を投入。投入前ゲート＝dupcheck_built 名前一致0・eventCd一致0／'
             'check_badges OK／check_order 違反0／CRLF bare-LF 0。'
             'reconcile --new＝OK70・MISSING/DROP/STALE/FETCH/QC 全0・QCカバレッジ89/91。'
             '翌朝(9/3)に①独立再照合②別エージェントの客観チェック→振り分け。'),
})
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('last_batch.json 更新  batches =', len(d['batches']))
