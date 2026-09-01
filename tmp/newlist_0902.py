# -*- coding: utf-8 -*-
"""9/1投入のぴあ新着103件の「id と ぴあURL」だけを出す。
別エージェントにゼロから再導出させるため、登録値（公演日・枠・県）は渡さない
（feedback_verify_independent_not_anchored）。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
rows = []
for e in EV:
    if e.get('genre') != 'new' or not (6070 <= e['id'] <= 6172):
        continue
    u = ((e.get('links') or {}).get('pia') or '')
    if not u:
        for t in (e.get('tickets') or []):
            if t.get('url'):
                u = t['url']
                break
    rows.append((e['id'], u))
half = (len(rows) + 1) // 2
for name, part in (('A', rows[:half]), ('B', rows[half:])):
    with open(f'tmp/verify_list_{name}_0902.txt', 'w', encoding='utf-8', newline='\n') as f:
        for i, u in part:
            f.write(f'{i}\t{u}\n')
    print(f'{name}: {len(part)}件 → tmp/verify_list_{name}_0902.txt')
print('URL空:', sum(1 for _, u in rows if not u))
