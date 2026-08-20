# -*- coding: utf-8 -*-
"""7/9 新着 再QC修正: 2265 チケット名の余計なピリオド除去 / 2270・2297 単日なのに範囲表記のdateLabel修正。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}
log = []

# 1) 2265 原田知世: "一般発売." -> "一般発売"
e = byid[2265]
for t in e['tickets']:
    if '一般発売.' in t.get('type', ''):
        old = t['type']; t['type'] = t['type'].replace('一般発売.', '一般発売')
        log.append('2265 ticket: %s -> %s' % (old, t['type']))

# 2) 2270 / 2297: dateLabel 単日範囲を単日へ
def collapse(dl):
    # "...年M月D日(曜)〜同...年M月D日(曜)..." で前後が同一なら片方に
    mo = re.match(r'(\d{4}年\d{1,2}月\d{1,2}日\([^)]+\))〜(\d{4}年\d{1,2}月\d{1,2}日\([^)]+\))(.*)', dl)
    if mo and mo.group(1) == mo.group(2):
        return mo.group(1) + mo.group(3)
    return dl
for i in (2270, 2297):
    e = byid[i]
    old = e.get('dateLabel', '')
    new = collapse(old)
    if new != old:
        e['dateLabel'] = new
        log.append('%d dateLabel: %s -> %s' % (i, old, new))

for l in log:
    print(' ', l)
if DRY:
    print('(DRY)')
else:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0709_fixqc2', 'w', encoding='utf-8').write(h)
    open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print('written (backup: index.html.bak_0709_fixqc2)')
