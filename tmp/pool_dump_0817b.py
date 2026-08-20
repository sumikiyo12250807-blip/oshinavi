# -*- coding: utf-8 -*-
"""新着プール(genre=="new")の現状を出す。振り分け前の材料。"""
import io, re, sys, json, collections
sys.stdout.reconfigure(encoding='utf-8')

idx = io.open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S).group(2))
pool = [e for e in EV if e.get('genre') == 'new']
print('新着プール %d件' % len(pool))
print('  _genre下書きの内訳:', dict(collections.Counter(e.get('_genre', '(なし)') for e in pool)))
print('  _piaSubの内訳    :', dict(collections.Counter((e.get('_piaSub') or '(空)') for e in pool)))
print()
out = []
for e in pool:
    t = (e.get('tickets') or [{}])[0]
    out.append({
        'id': e['id'], 'artist': e.get('artist', ''), 'name': e.get('name', ''),
        '_genre': e.get('_genre', ''), '_piaGenre': e.get('_piaGenre', ''), '_piaSub': e.get('_piaSub', ''),
        'venue': e.get('venue', ''), 'prefecture': e.get('prefecture', ''),
        'date': e.get('date', ''), 'desc': (e.get('description') or '')[:120],
        'url': (e.get('links') or {}).get('pia') or (e.get('links') or {}).get('official') or t.get('url', ''),
    })
json.dump(out, io.open('tmp/pool_0817b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for o in out:
    print('%5d [%-8s] pia=%-10s/%-12s %s | %s %s' % (
        o['id'], o['_genre'] or '-', o['_piaGenre'] or '-', o['_piaSub'] or '-',
        o['artist'][:30], o['prefecture'], o['date']))
print('\n→ tmp/pool_0817b.json')
