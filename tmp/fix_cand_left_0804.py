# -*- coding: utf-8 -*-
"""候補名の連続スペースを1つに詰める（ぴあのtitle由来の二重スペース）。"""
import io
import json
import re

p = 'tmp/cand_left_0804.json'
c = json.load(io.open(p, encoding='utf-8'))
for x in c:
    x['artist'] = re.sub(r'\s{2,}', ' ', x['artist']).strip()
json.dump(c, io.open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('normalized %d names' % len(c))
