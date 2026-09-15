# -*- coding: utf-8 -*-
"""組み上がり（build_pia_entries の出力）を1行ずつ並べる（読むだけ・2026-09-15夜）。
使い方: python tmp/x0916/built_summary.py tmp/x0916/built_merge.json [tmp/x0916/built_new.json ...]
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
for p in sys.argv[1:]:
    raw = io.open(p, encoding='utf-8').read().strip()
    arr = json.loads(raw) if raw else []
    print('■ %s  %d件' % (p, len(arr)))
    for b in arr:
        ts = b.get('tickets') or []
        print('  id%s ｜%s ｜%s ｜%s ｜枠%d ｜%s' % (
            b['id'], (b.get('name') or '')[:34], b.get('prefecture'), b.get('dateLabel', '')[:28], len(ts),
            ' / '.join((t.get('type') or '')[:40] for t in ts[:3])))
