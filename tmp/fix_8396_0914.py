# -*- coding: utf-8 -*-
"""8396 Billyrrom＝日付の欄が「11/14〜R9年 3/7・北海道・広島・静岡・愛知」のまま、枠（昼のヒールで16枠）は
11/7 宮城〜R9年 3/21 東京・11県に広がった＝照合の QC-EVDATE（ev.date が実公演の千秋楽より古い＝3/7 で画面から消える）。
これからの公演は枠の（…公演）から数えた＝11/7 宮城・11/14 静岡・11/23 香川・12/4 広島・12/5 熊本・12/12 栃木・12/19 石川・
R9年 2/20 福岡・2/28 愛知・3/7 北海道・3/21 東京。5県以上は「全国」。会場の一覧は触らない（嘘にはなっていない）。
使い方: python tmp/fix_8396_0914.py [--apply]
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 8396)
assert e['date'] == '2027-03-07', e['date']
new = {'date': '2027-03-21', 'dateLabel': '2026年11月7日(土)〜2027年3月21日(日) 全国', 'prefecture': '全国'}
for k, v in new.items():
    print('%-10s %s → %s' % (k, e.get(k), v))
    e[k] = v
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
