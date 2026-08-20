# -*- coding: utf-8 -*-
"""7/9 既存の「本日発売で崩れてる」27件を再取得し締切日を取り込む(genre不変・ticketのみ更新)。"""
import sys, json, re
sys.path.insert(0, 'tools')
import build_pia_entries as bpe
from build_pia_entries import build

IDS = [708,863,1122,1123,1813,1851,1852,1853,1856,1992,1993,1994,1995,1996,1997,
       1998,1999,2000,2001,2002,2156,2200,2205,2234,2235,2236,2259]

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
    if not ev:
        out.append({'id': i, 'status': 'MISSING'}); continue
    urls = pia_urls(ev)
    if not urls:
        out.append({'id': i, 'status': 'NO_PIA'}); sys.stderr.write(f"  {i} NO_PIA\n"); continue
    cand = {'newid': i, 'artist': ev.get('artist', ''), 'urls': urls}
    try:
        ne = build(cand)
    except Exception as ex:
        out.append({'id': i, 'status': 'ERROR', 'err': str(ex)[:100]})
        sys.stderr.write(f"  {i} ERROR {ex}\n"); continue
    if ne is None:
        out.append({'id': i, 'status': 'delete', 'artist': ev.get('artist', '')})
        sys.stderr.write(f"  {i} DELETE(買える枠0) {ev.get('artist','')[:20]}\n")
    else:
        out.append({'id': i, 'status': 'convert', 'artist': ev.get('artist', ''),
                    'tickets': ne['tickets'], 'date': ne['date'], 'dateLabel': ne['dateLabel'],
                    'venue': ne['venue'], 'prefecture': ne['prefecture']})
        sys.stderr.write(f"  {i} convert {len(ne['tickets'])}枠  {ne['tickets'][0]['type'][:44]}\n")

json.dump(out, open('tmp/convert_existing_flip_0709.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
nc = sum(1 for o in out if o['status'] == 'convert')
nd = sum(1 for o in out if o['status'] == 'delete')
sys.stderr.write(f"\n=== convert {nc} / delete {nd} / total {len(IDS)} ===\n")
