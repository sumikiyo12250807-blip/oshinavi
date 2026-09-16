# -*- coding: utf-8 -*-
"""built2.log から組み立て結果のJSONだけを取り出す（2026-09-16 夜）。
2>&1 でまとめてしまったので、進捗行（"  11049 OK"）と末尾の要約が混ざっている。
ぴあを29ページ叩き直すのは避けたいので、行単位で JSON の範囲を切り出して検算する。
使い方: python tmp/x0917/extract_built2.py
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

lines = io.open('tmp/x0917/built2.log', encoding='utf-8', errors='replace').read().splitlines()
start = next(i for i, ln in enumerate(lines) if ln.strip() == '[')
end = max(i for i, ln in enumerate(lines) if ln.startswith(']'))
body = lines[start:end] + [']']
data = json.loads('\n'.join(body))
ids = [e['id'] for e in data]
slots = sum(len(e.get('tickets') or []) for e in data)
io.open('tmp/x0917/built2.json', 'w', encoding='utf-8').write(
    json.dumps(data, ensure_ascii=False, indent=1))
print('entries=%d slots=%d ids=%s' % (len(data), slots, ids))
assert len(data) == 19, len(data)
assert all(e.get('tickets') for e in data), 'tickets empty'
