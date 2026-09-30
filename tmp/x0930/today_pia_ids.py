# -*- coding: utf-8 -*-
# 夜のヒールを短くする：今日発売（startDate==今日）の枠を持つ「ぴあ」のエントリだけ id を出す
# 使い方: python tmp/x0930/today_pia_ids.py [YYYY-MM-DD]  → tmp/x0930/today_pia_ids.txt
import datetime, io, json, sys
day = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
s = io.open('index.html', encoding='utf-8').read()
i = s.index('const EVENTS = [') + len('const EVENTS = ')
E, _ = json.JSONDecoder().raw_decode(s[i:])
ids = []
for e in E:
    pia = bool((e.get('links') or {}).get('pia'))
    for t in e.get('tickets') or []:
        u = t.get('url') or ''
        if t.get('startDate') == day and not t.get('soldout') and ('pia.jp' in u or (not u and pia)):
            ids.append(e['id'])
            break
io.open('tmp/x0930/today_pia_ids.txt', 'w', encoding='utf-8').write(','.join(map(str, ids)))
print(day, 'ぴあの今日発売を持つエントリ', len(ids))
