# -*- coding: utf-8 -*-
"""枠0の67件が「なぜ画面から枠が消えているか」をローカルで分類する。
ぴあを叩く前に、叩かなくても分かることを先に片づける。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = '2026-09-10'
IDS = [125,1554,2752,2864,3085,3287,3418,3510,3531,3696,3994,4051,4057,4059,4077,4081,
       4084,4085,4087,4089,4092,4095,4099,4100,4104,4106,4107,4108,4113,4121,4259,4329,
       4351,4373,4387,4394,4396,4397,4404,4406,4410,4414,4418,4436,4870,4951,4952,4953,
       4955,4956,4958,5154,5156,5157,5433,5669,5719,5721,5722,5723,6094,6109,6233,6261,
       6420,6615,6922]

h = io.open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))}

buckets = {}
for i in IDS:
    e = ev.get(i)
    if not e:
        continue
    ts = e.get('tickets') or []
    past = [t for t in ts if (t.get('date') or '9999') < TODAY]
    future_start = [t for t in ts if (t.get('startDate') or '') > TODAY]
    reasons = []
    if ts and len(past) == len(ts):
        reasons.append('登録枠が全部「締切が過去」')
    if future_start:
        reasons.append('発売開始がまだ先')
    if not ts:
        reasons.append('枠そのものが無い')
    key = ' / '.join(reasons) or 'その他'
    buckets.setdefault(key, []).append(i)

for k, v in sorted(buckets.items(), key=lambda x: -len(x[1])):
    print('■ %s … %d件' % (k, len(v)))
    print('   ' + ','.join(map(str, v)))
    print()

# 「締切が全部過去」の子の、いちばん新しい締切を見る＝どれだけ古いか
print('--- 締切が全部過去の子：いちばん新しい締切 ---')
for i in buckets.get('登録枠が全部「締切が過去」', [])[:70]:
    e = ev[i]
    last = max((t.get('date') or '') for t in e['tickets'])
    print('  id%-5d 最終締切%s 公演%s  %s' % (i, last, e.get('date'), (e.get('name') or '')[:32]))
