# -*- coding: utf-8 -*-
"""指定した楽天URLを build_rakuten_entries が食える形（recのリスト）に引き直す。

  python tmp/rakuten_fetch_recs_0910.py tmp/rakuten_presale_fresh_0910.json tmp/rakuten_recs_0910.json
"""
import io
import json
import sys
import time

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as RH

SRC, OUT = sys.argv[1], sys.argv[2]
urls = json.load(io.open(SRC, encoding='utf-8'))
recs, bad = [], []
for i, u in enumerate(urls, 1):
    try:
        r = RH.parse_page(u, RH.fetch(u))
    except Exception as ex:
        bad.append((u, repr(ex)[:60]))
        continue
    if not r.get('name') or not r.get('perfs'):
        bad.append((u, '公演が読めない'))
        continue
    recs.append(r)
    time.sleep(0.4)

json.dump(recs, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('引けた %d件 / 読めない %d件 → %s' % (len(recs), len(bad), OUT))
for u, w in bad:
    print('  ⏭️ %s %s' % (w, u))
