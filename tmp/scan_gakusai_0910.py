# -*- coding: utf-8 -*-
"""genre=gakusai（学園祭）のエントリを並べる。学園祭でないものが紛れていないか見るため。

きっかけ＝2026-09-09 夜にユーザーが発見。id6972 ハナレグミが gakusai になっていた。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))

# 学園祭らしい語。これが名前にも会場にも無ければ「学園祭ではない疑い」
WORDS = ['学園祭', '大学祭', '学祭', '文化祭', '学院祭', '祭典', '大学', '学園', '学院',
         'キャンパス', '高校', '短大', '専門学校', 'カレッジ', '大学院']

rows = [e for e in events if e.get('genre') == 'gakusai']
sus = []
for e in rows:
    hay = '%s %s %s' % (e.get('name') or '', e.get('venue') or '', e.get('dateLabel') or '')
    if not any(w in hay for w in WORDS):
        sus.append(e)

with open('tmp/gakusai_0910.txt', 'w', encoding='utf-8') as f:
    f.write('genre=gakusai %d件 / 学園祭らしい語が無い %d件\n' % (len(rows), len(sus)))
    for e in sorted(sus, key=lambda x: x['id']):
        ls = e.get('links') or {}
        u = ls.get('pia') or ls.get('eplus') or ls.get('rakuten') or ls.get('lawson') or ''
        f.write('\nid=%-5s %s\n   会場=%s\n   %s\n'
                % (e['id'], e['name'][:60], (e.get('venue') or '')[:60], u))
print('genre=gakusai %d件 / 学園祭らしい語が無い %d件 → tmp/gakusai_0910.txt' % (len(rows), len(sus)))
