# -*- coding: utf-8 -*-
"""枠を足したら会期の外に公演が出た3件の会期・会場・県を、ぴあ実ページのビルド結果に合わせる
（[[feedback_show_true_dates_not_sellable_range]]・date は千秋楽＝伸ばさないと足した公演の前にカードが消える）。
  3722 イリーナ・メジューエワ … 初日は今のラベル（2026/9/13）のまま、千秋楽をビルドの 2027/12/11 へ
  5732 SION'S SQUAD / 5027 OSAKA COMEDY FESTIVAL … ビルドの会期・会場・県をそのまま使う"""
import datetime, io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
WD = '月火水木金土日'
b = {e['id']: e for e in json.load(io.open('tmp/built_missE_0911.json', encoding='utf-8-sig'))}
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
ev = json.loads(m.group(2))
for e in ev:
    i = e['id']
    if i == 3722:
        y, mo, d = map(int, b[i]['date'].split('-'))
        end = '%d年%d月%d日(%s)' % (y, mo, d, WD[datetime.date(y, mo, d).weekday()])
        old = e['dateLabel']
        e['dateLabel'] = re.sub(r'〜\d{4}年\d{1,2}月\d{1,2}日\([^)]*\)', '〜' + end, old, count=1)
        e['date'] = b[i]['date']
        print(i, old, '→', e['dateLabel'], e['date'])
    elif i in (5732, 5027):
        for k in ('date', 'dateLabel', 'venue', 'prefecture'):
            print(i, k, e.get(k), '→', b[i].get(k))
            e[k] = b[i].get(k)
open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + json.dumps(ev, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
