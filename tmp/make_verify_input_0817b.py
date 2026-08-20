# -*- coding: utf-8 -*-
"""独立検証エージェントに渡す素材。あたしの判定(_genre)は入れない
（[[feedback_verify_independent_not_anchored]]＝アンカーを与えずゼロから再導出させる）。"""
import io, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')

idx = io.open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S).group(2))
out = []
for e in EV:
    if e.get('genre') != 'new' or not (4426 <= e['id'] <= 4488):
        continue
    out.append({
        'id': e['id'],
        'artist': e.get('artist', ''),
        'venue': e.get('venue', ''),
        'prefecture': e.get('prefecture', ''),
        'showDate': e.get('date', ''),
        'piaCategory': e.get('_piaSub') or '(取得できず)',
        'url': (e.get('links') or {}).get('pia', ''),
    })
json.dump(out, io.open('tmp/verify_input_0817b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('%d件 → tmp/verify_input_0817b.json' % len(out))
