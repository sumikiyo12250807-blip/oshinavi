# -*- coding: utf-8 -*-
"""全エントリを走査し、表示が崩れうるチケットを分類する。
崩れパターン = startDateあり かつ date==startDate（発売前フォームのまま＝販売終了日が未取込）。
- date==startDate < today   : 発売日を過ぎた＝check_expiredが翌朝救済（既知healルート）
- date==startDate == today  : 本日発売＝発売時刻後に「販売中〜発売日」に崩れる（要同日対応）
- date==startDate > today   : まだ発売前で正常（発売日にカウントダウン中・将来崩れる予備軍）
"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TODAY = '2026-07-09'
h = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S).group(1))
past=today=future=0
today_list=[]
for e in EVENTS:
    for t in e.get('tickets', []):
        sd = t.get('startDate'); d = t.get('date')
        if not sd or sd != d:      # 販売終了日が別に入ってる＝正常
            continue
        if t.get('saleUntilSoldOut'):
            continue
        if d < TODAY:
            past += 1
        elif d == TODAY:
            today += 1
            today_list.append((e['id'], e.get('genre'), e['artist'][:26]))
        else:
            future += 1
print('== date==startDate（販売終了日 未取込）の枠数 ==')
print('  発売日<今日 (翌朝救済ルート/既知)   :', past)
print('  発売日==今日 (本日発売・要同日対応) :', today)
print('  発売日>今日 (まだ発売前・将来予備軍):', future)
print('\n-- 本日発売で崩れうる子 --')
for i,g,a in today_list:
    print('  id=%d [%s] %s' % (i,g,a))
