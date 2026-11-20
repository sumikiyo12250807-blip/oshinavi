# -*- coding: utf-8 -*-
# index.html（読むだけ）から FANY 9500（ルミネ 年末特別公演）・22502（コットン）を含むエントリの id・名前・11/12 の枠を探す
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
L = io.open('C:/Users/user/oshinavi/index.html', encoding='utf-8').read().splitlines()
last_id = None
seen = set()
for i, l in enumerate(L):
    m = re.search(r'"id":\s*(\d+)', l)
    if m:
        last_id = (int(m.group(1)), i)
    for key in ('detail/9500', 'detail/10375', 'detail/22502'):
        if key in l and last_id and (key, last_id[0]) not in seen and i > 20000:
            seen.add((key, last_id[0]))
            blk = '\n'.join(L[last_id[1]:last_id[1] + 6])
            print(key, last_id[0], '|', re.sub(r'\s+', ' ', blk)[:300])
