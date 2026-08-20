# -*- coding: utf-8 -*-
"""救済4件(1425/2139/2310/2320)をぴあ機械パースで再構築し、tickets等を確認する"""
import sys, json, re
sys.path.insert(0, 'tools')
import build_pia_entries as B

src = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\n\s*\]);', src, re.S)
events = json.loads(m.group(1))
by_id = {e['id']: e for e in events}

out = {}
for eid in (1425, 2139, 2310, 2320):
    e = by_id[eid]
    url = (e.get('links') or {}).get('pia')
    cand = {'newid': eid, 'artist': e['artist'], 'name': e['name'], 'urls': [url]}
    try:
        out[eid] = {'url': url, 'now': e, 'built': B.build(cand)}
    except Exception as ex:
        out[eid] = {'url': url, 'now': e, 'error': repr(ex)[:300]}

with open('tmp/rescue_0727.json', 'w', encoding='utf-8') as f:
    json.dump({'result': out, 'dropped': B._DROPPED}, f, ensure_ascii=False, indent=2)
