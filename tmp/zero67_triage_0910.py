# -*- coding: utf-8 -*-
"""枠0の67件を、叩く前にローカルで仕分ける。

🚨reconcile_pia は**ぴあ専用**＝ぴあ外リンクの子に使っても答えは出ない
（[[feedback_delete_nonpia_blindspot]]）。先に売り場で分けてから当たる。
"""
import io
import json
import re
import sys
from datetime import date

sys.stdout.reconfigure(encoding='utf-8')
IDS = [125,1554,2752,2864,3085,3287,3418,3510,3531,3696,3994,4051,4057,4059,4077,4081,
       4084,4085,4087,4089,4092,4095,4099,4100,4104,4106,4107,4108,4113,4121,4259,4329,
       4351,4373,4387,4394,4396,4397,4404,4406,4410,4414,4418,4436,4870,4951,4952,4953,
       4955,4956,4958,5154,5156,5157,5433,5669,5719,5721,5722,5723,6094,6109,6233,6261,
       6420,6615,6922]

h = io.open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))}
today = date.today().isoformat()

buckets = {}
for i in IDS:
    e = ev.get(i)
    if not e:
        buckets.setdefault('消えている', []).append((i, ''))
        continue
    L = e.get('links') or {}
    vend = [k for k in ('pia', 'rakuten', 'eplus', 'lawson', 'fany', 'yoshimoto',
                        'tvasahi', 'shochiku', 'official') if L.get(k)]
    soldout = any('予定枚数終了' in (t.get('type') or '') or t.get('soldout') for t in e.get('tickets') or [])
    key = ('売り切れ表示あり' if soldout else ('/'.join(vend) or 'リンク無し'))
    buckets.setdefault(key, []).append((i, e))

for k in sorted(buckets, key=lambda x: -len(buckets[x])):
    rows = buckets[k]
    print('■ %s … %d件' % (k, len(rows)))
    for i, e in rows[:60]:
        if not e:
            print('   id%-5d (EVENTSに無い)' % i)
            continue
        nt = len(e.get('tickets') or [])
        print('   id%-5d 公演%s %-34s 枠%d %s'
              % (i, e.get('date'), (e.get('name') or '')[:34], nt, e.get('genre')))
    print()
