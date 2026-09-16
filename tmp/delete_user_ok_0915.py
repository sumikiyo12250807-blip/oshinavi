# -*- coding: utf-8 -*-
"""ユーザーが「消していい」と決めたエントリを index.html から消す（2026-09-15 朝）。
対象＝7946 源 上映会・6109 三三・左龍の会（ぴあのページが無効・ほかの売り場も見つからない＝売っていることが確かめられない）。
ユーザーの言葉「消していいわ　売ってないってことよね　すぐ消して」（9/15 09:3x）。
URLは index.html から機械抽出する（手で書かない）。NEW_ORDER からも外す。改行は CRLF を保つ。
使い方: python tmp/delete_user_ok_0915.py <id,id,...> [--apply]
"""
import datetime
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today()
IDS = [int(x) for x in sys.argv[1].split(',') if x.strip()]
APPLY = '--apply' in sys.argv

src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
byid = {e['id']: e for e in events}

rows = []
for i in IDS:
    e = byid.get(i)
    if not e:
        print('  id%s はエントリが無い' % i)
        continue
    ls = e.get('links') or {}
    url = ls.get('pia') or ls.get('eplus') or ls.get('rakuten') or ls.get('lawson') or ''
    if not url:
        url = next((t.get('url') for t in (e.get('tickets') or []) if t.get('url')), '')
    rows.append((i, e.get('name') or '', e.get('date') or '', e.get('venue') or '', e.get('genre'), url))
for r in rows:
    print('  id=%-5s %s (%s) genre=%s %s' % (r[0], r[1][:44], r[2], r[4], r[5]))
if not APPLY:
    print('（--apply を付けると実際に消す）')
    sys.exit(0)

kill = {r[0] for r in rows}
left = [e for e in events if e['id'] not in kill]
assert len(events) - len(left) == len(kill), '消える数が合わない'
bak = 'index.html.bak_%s_del_user' % TODAY.strftime('%m%d')
open(bak, 'w', encoding='utf-8', newline='').write(src)
nl = '\r\n' if '\r\n' in src else '\n'
arr = json.dumps(left, ensure_ascii=False, indent=2).replace('\n', nl)
out = src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():]
mo = re.search(r'const NEW_ORDER = \[([^\]]*)\];', out)
if mo:
    order = [int(x) for x in mo.group(1).split(',') if x.strip()]
    order2 = [x for x in order if x not in kill]
    if order2 != order:
        out = out[:mo.start()] + 'const NEW_ORDER = [%s];' % ', '.join(str(x) for x in order2) + out[mo.end():]
open('index.html', 'w', encoding='utf-8', newline='').write(out)

log = 'logs/removed_%s.md' % TODAY.isoformat()
with open(log, 'a', encoding='utf-8') as f:
    f.write('\n## ユーザーの決定で消した（%d件）\n\n' % len(rows))
    f.write('ぴあのページが無効になり、ほかの売り場（e+・楽天・ローチケ）も見つからない＝売っていることが確かめられない。'
            'ユーザー「消していいわ　売ってないってことよね　すぐ消して」（9/15 朝）。\n\n')
    f.write('| id | 公演名 | 公演日 | 会場 | 確認用URL |\n|---|---|---|---|---|\n')
    for i, n, d, v, g, u in rows:
        f.write('| %s | %s | %s | %s | %s |\n' % (i, n.replace('|', '／'), d, v.replace('|', '／'), u))
print('%d件を削除（backup: %s ／ 記録: %s ／ 残り %d件）' % (len(rows), bak, log, len(left)))
