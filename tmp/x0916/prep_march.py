# -*- coding: utf-8 -*-
"""第54回 関西マーチングコンテストの会場の席（ぴあ 2634965）を、配信だけのエントリ 7156 に畳んだのは誤り＝7156 から外し、
別の新規エントリとして新着に入れる（2026-09-15夜）。組み上がり 90021 の id を 10719 に付け替えるだけ。
使い方: python tmp/x0916/prep_march.py
出力: tmp/x0916/inject_march.json
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
built = {b['id']: b for b in json.load(io.open('tmp/x0916/built_misc_0915.json', encoding='utf-8'))}
src = io.open('index.html', encoding='utf-8').read()
ids = {e['id'] for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
NEW_ID = 10719
assert NEW_ID not in ids, 'id%s はもう使われている' % NEW_ID
b = dict(built[90021])
b['id'] = NEW_ID
json.dump([b], io.open('tmp/x0916/inject_march.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('id%s %s ｜ %s ｜ %s ｜ 枠%d' % (NEW_ID, b.get('name'), b.get('venue'), b.get('dateLabel'), len(b.get('tickets') or [])))
