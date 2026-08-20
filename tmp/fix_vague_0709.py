# -*- coding: utf-8 -*-
"""曖昧券種3件に締切〜7/9を追記(発売中の締切明示)。全部ぴあ/e+で〜7/9 23:59確認済。"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

# 326 キム・ジョンヒョン
for t in byid[326]['tickets']:
    if t['type'] == '一般発売' and t['date'] == '2026-07-09':
        t['type'] = '一般発売（東京 7/18公演）〜7/9 23:59'
# 185 斉藤朱夏 愛知公演のみ
for t in byid[185]['tickets']:
    if t['type'] == '愛知公演 一般発売' and t['date'] == '2026-07-09':
        t['type'] = '愛知公演 一般発売 〜7/9 23:59'
# 449 小林よしひさ
for t in byid[449]['tickets']:
    if t['type'] == '一般発売（追加公演）' and t['date'] == '2026-07-09':
        t['type'] = '一般発売（追加公演 7/12）〜7/9 23:59'

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html.bak_0709_fixvague', 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('修正完了:')
for i in [326, 185, 449]:
    for t in byid[i]['tickets']:
        if t['date'] == '2026-07-09':
            print('  id=%d -> %s' % (i, t['type']))
