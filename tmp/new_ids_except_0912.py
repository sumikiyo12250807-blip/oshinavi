# -*- coding: utf-8 -*-
"""新着プール（genre:new）の id を、指定した id を除いてカンマ区切りで出す（読むだけ）。
tools/assign_genres.py はプール全部を振り分けるので、今夜は 8345・8346 だけを振り分けるために、残りを --exclude に渡す。
（9/12に入れた他の新着は、決まりどおり明朝の再チェックのあとで振り分ける）
使い方: python tmp/new_ids_except_0912.py 8345,8346
"""
import io
import json
import re
import sys

keep = {int(x) for x in sys.argv[1].split(',') if x}
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
ids = [e['id'] for e in ev if e.get('genre') == 'new']
missing = sorted(keep - set(ids))
if missing:
    sys.stderr.write('プールに無いid: %s\n' % missing)
    sys.exit(2)
print(','.join(str(i) for i in ids if i not in keep))
sys.stderr.write('プール %d件 ／ 振り分ける %d件 ／ 外す %d件\n' % (len(ids), len(keep), len(ids) - len(keep)))
