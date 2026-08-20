# -*- coding: utf-8 -*-
"""7/9 本日発売16件を再取得。発売開始した枠の締切日(〜M/D)を取り込む。
build_pia_entriesでぴあ現状態を機械再パース→convert_today_0709.json出力。"""
import sys, json, re
sys.path.insert(0, 'tools')
import build_pia_entries as bpe
from build_pia_entries import build

IDS = [2251,2252,2253,2255,2257,2258,2259,2260,2261,2262,2263,2276,2277,2278,2279,2280]

def pia_urls(ev):
    urls = []
    p = (ev.get('links') or {}).get('pia')
    if p and 'pia' in p:
        urls.append(p)
    for t in ev.get('tickets', []):
        u = t.get('url')
        if u and 'pia' in u and u not in urls:
            urls.append(u)
    return urls

h = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S).group(1))
byid = {e['id']: e for e in EVENTS}

out = []
for i in IDS:
    ev = byid.get(i)
    urls = pia_urls(ev)
    cand = {'newid': i, 'artist': ev.get('artist', ''), 'urls': urls}
    try:
        ne = build(cand)
    except Exception as ex:
        out.append({'id': i, 'status': 'ERROR', 'artist': ev.get('artist', ''), 'err': str(ex)[:120]})
        sys.stderr.write(f"  {i} ERROR {ex}\n"); continue
    if ne is None:
        out.append({'id': i, 'status': 'delete', 'artist': ev.get('artist', '')})
        sys.stderr.write(f"  {i} DELETE {ev.get('artist','')[:20]}\n")
    else:
        out.append({'id': i, 'status': 'convert', 'artist': ev.get('artist', ''),
                    'tickets': ne['tickets'], 'date': ne['date'], 'dateLabel': ne['dateLabel'],
                    'venue': ne['venue'], 'prefecture': ne['prefecture']})
        # 変化サマリ
        old_ends = [t.get('type','') for t in ev.get('tickets', [])]
        new_ends = [t.get('type','') for t in ne['tickets']]
        sys.stderr.write(f"  {i} convert {len(ne['tickets'])}枠  {ne['tickets'][0]['type'][:40]}\n")

json.dump(out, open('tmp/convert_today_0709.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
nc = sum(1 for o in out if o['status'] == 'convert')
sys.stderr.write(f"\n=== convert {nc}/{len(IDS)} ===\n")
