# -*- coding: utf-8 -*-
"""統合行きのうち「同じ名前の既存エントリが2つ以上」で足す先を決め切れなかった分（tmp/merge_map_0912.json の target=None）を、
ビルド用の候補ファイルにする（読むだけ・tmpに書く）。どちらの既存ツアーに足すかは、ビルドして会場・公演日を見てから決める。
1件1URL・仮id は 99301 から。
使い方: python tmp/hold_same2_cands_0912.py
出力: tmp/cand_same2_0912.json
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
rows = json.load(io.open('tmp/merge_map_0912.json', encoding='utf-8'))
out, n = [], 99301
for r in rows:
    if r.get('target') is not None:
        continue
    out.append({'newid': n, 'artist': r['artist'], 'urls': [r['url']], 'eventCd': r['eventCd'], 'cands': r.get('cands')})
    n += 1
json.dump(out, io.open('tmp/cand_same2_0912.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for o in out:
    print('  %s %s | 既存の候補=%s' % (o['newid'], o['artist'], o['cands']))
print('保留7件の候補 %d件 → tmp/cand_same2_0912.json' % len(out))
