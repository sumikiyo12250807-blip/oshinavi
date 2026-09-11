# -*- coding: utf-8 -*-
"""統合行きのうち足す先が1つに決まった分を、ビルド用の候補ファイルにする（読むだけ・tmpに書く）。
1件1URL（2本目以降に ticket.url が付かない穴を避ける）。仮id は 99201 から。target＝足す先の既存id。
merge_with_urls_0912.py は cands の target を見て足すので、同じ相手に複数来てもURLを取り違えない。
使い方: python tmp/merge_cands_0912.py
出力: tmp/cand_mergeY_0912.json
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
rows = json.load(io.open('tmp/merge_map_0912.json', encoding='utf-8'))
out, n = [], 99201
for r in rows:
    if r.get('target') is None:
        continue
    out.append({'newid': n, 'target': r['target'], 'artist': r['artist'], 'urls': [r['url']],
                'eventCd': r['eventCd'], 'rlsdate': r.get('rlsdate')})
    n += 1
json.dump(out, io.open('tmp/cand_mergeY_0912.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('統合の候補 %d件（仮id 99201〜%d）→ tmp/cand_mergeY_0912.json' % (len(out), n - 1))
