# -*- coding: utf-8 -*-
"""候補ファイルから指定の newid だけを抜き出す（読むだけ・2026-09-15）。混雑ページで組めなかった分の組み直し用。
使い方: python tmp/pick_cands_0915.py <元の候補.json> <newid,newid,...> <出力.json>
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
src, ids, dst = sys.argv[1], {int(x) for x in sys.argv[2].split(',') if x.strip()}, sys.argv[3]
rows = [c for c in json.load(io.open(src, encoding='utf-8')) if c['newid'] in ids]
json.dump(rows, io.open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('%d件 → %s' % (len(rows), dst))
