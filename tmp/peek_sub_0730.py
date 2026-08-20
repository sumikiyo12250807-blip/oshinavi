# -*- coding: utf-8 -*-
"""下書きが怪しい数件の _piaSub を確認（ぴあのカテゴリを見て相談材料にする）。"""
import json
import re

IDS = [3510, 3511, 3512, 3513, 3505, 3507, 3480]
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}
out = []
for i in IDS:
    e = byid[i]
    out.append(f"id={i} _genre={e.get('_genre')} _extra={e.get('_extraGenres')} _piaSub={e.get('_piaSub') or '(空)'}")
    out.append(f"    {e.get('artist')}")
    out.append(f"    venue={e.get('venue')}")
open('tmp/peek_sub_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/peek_sub_0730.txt')
