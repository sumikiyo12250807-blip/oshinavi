# -*- coding: utf-8 -*-
"""検証エージェント用の入力を作る。**登録値は一切渡さない**（アンカリング防止＝
[[feedback_verify_independent_not_anchored]]）。渡すのは id と ぴあURL だけ。"""
import re, io, json, sys
sys.stdout.reconfigure(encoding='utf-8')

s = io.open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS\s*=\s*(\[)', s)
i = m.start(1); d = 0
for j in range(i, len(s)):
    if s[j] == '[': d += 1
    elif s[j] == ']':
        d -= 1
        if d == 0: break
ev = json.loads(s[i:j + 1])
new = [e for e in ev if e.get('genre') == 'new']
new.sort(key=lambda e: e['id'])

rows = [{'id': e['id'], 'pia': (e.get('links') or {}).get('pia')} for e in new]
half = (len(rows) + 1) // 2
for k, part in enumerate([rows[:half], rows[half:]], 1):
    p = 'tmp/verify_in_%d_0825.json' % k
    json.dump(part, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(p, len(part), '件  id', part[0]['id'], '〜', part[-1]['id'])

# 突合用に登録値も別ファイルへ（エージェントには渡さない・親が差分を取るためだけ）
ref = {}
for e in new:
    ref[str(e['id'])] = {
        'name': e.get('name'), 'date': e.get('date'),
        'prefecture': e.get('prefecture'), 'venue': e.get('venue'),
        'tickets': [{'type': t.get('type'), 'date': t.get('date')} for t in e.get('tickets') or []],
    }
json.dump(ref, open('tmp/verify_ref_0825.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('ref written: tmp/verify_ref_0825.json')
