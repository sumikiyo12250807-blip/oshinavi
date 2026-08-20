# -*- coding: utf-8 -*-
"""全エントリ走査。date==startDate（販売終了日 未取込）の枠を分類。
発売日==今日 = 本日発売 → 再buildで締切取込が必要(朝ルーチン常設)。"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TODAY = '2026-07-10'
h = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S).group(1))
past=today=future=0
today_list=[]; past_list=[]
for e in EVENTS:
    for t in e.get('tickets', []):
        sd = t.get('startDate'); d = t.get('date')
        if not sd or sd != d:
            continue
        if t.get('saleUntilSoldOut'):
            continue
        if d < TODAY:
            past += 1; past_list.append((e['id'], e['artist'][:26], d))
        elif d == TODAY:
            today += 1
            today_list.append((e['id'], e.get('genre'), e['artist'][:26]))
        else:
            future += 1
print('== date==startDate（販売終了日 未取込）の枠数 ==')
print('  発売日<今日 (取りこぼし・要救済)    :', past)
print('  発売日==今日 (本日発売・要再build)  :', today)
print('  発売日>今日 (まだ発売前・正常)      :', future)
print('\n-- 本日発売で崩れうる子 --')
for i,g,a in today_list:
    print('  id=%d [%s] %s' % (i,g,a))
print('\n-- 発売日が過去のまま(取りこぼし) --')
for i,a,d in past_list:
    print('  id=%d %s (%s)' % (i,a,d))
ids = sorted(set([i for i,_,_ in today_list] + [i for i,_,_ in past_list]))
print('\nIDS =', ids)
