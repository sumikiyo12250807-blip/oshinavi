# -*- coding: utf-8 -*-
"""楽天由来の新着で「全国ツアー（…）」形の会場が4つで打ち切られていないか再パースで検証"""
import sys, io, re, json
sys.path.insert(0, 'tools')
import rakuten_harvest as H

src = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\n\s*\]);', src, re.S)
events = json.loads(m.group(1))
targets = [e for e in events
           if e.get('_srcgenre') == 'rakuten'
           and (e.get('venue') or '').startswith('全国ツアー（')]

out = []
for e in targets:
    url = None
    rk = (e.get('links') or {}).get('rakuten') or ''
    mm = re.search(r'murl=(.+)$', rk)
    if mm:
        url = __import__('urllib.parse', fromlist=['unquote']).unquote(mm.group(1))
    rec = {}
    venues = []
    if url:
        body = H.fetch(url)
        rec = H.parse_page(url, body)
        today = '2026-07-26'
        for p in rec.get('perfs', []):
            if (p.get('end') or p['date']) >= today and p['venue'] and p['venue'] not in venues:
                venues.append(p['venue'])
    cur = re.match(r'全国ツアー（(.*)）$', e['venue'])
    cur_v = cur.group(1).split('／') if cur else []
    out.append({
        'id': e['id'], 'name': e['name'], 'url': url,
        '登録会場数': len(cur_v), '実会場数': len(venues),
        '実会場': venues, '登録会場': cur_v,
    })

with open('tmp/rakuten_venue_fix.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print('対象', len(targets), '件 → tmp/rakuten_venue_fix.json')
for o in out:
    print(f"  id{o['id']} 登録{o['登録会場数']} / 実{o['実会場数']}  {o['name']}")
