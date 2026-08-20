# -*- coding: utf-8 -*-
"""7/10 期限切れ→販売中 変換(構築側)。check_expired ⚠️24件+削除候補1件を機械再パース。
買える枠ゼロ(None)=売切/終了=削除候補。tmp/convert_0710.json出力。"""
import sys, json, re
sys.path.insert(0, 'tools')
import build_pia_entries as bpe
from build_pia_entries import build

IDS = [38, 125, 217, 326, 372, 449, 499, 555, 610, 853, 860, 1142, 1162, 1200,
       1240, 1322, 1385, 1481, 1485, 1508, 1521, 1671, 1993, 2162, 2259]

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
        out.append({'id': i, 'status': 'MISSING_IN_DB'}); continue
    urls = pia_urls(ev)
    if not urls:
        out.append({'id': i, 'status': 'NO_PIA_URL', 'artist': ev.get('artist', ''), 'venue': ev.get('venue', '')})
        sys.stderr.write(f"  {i} NO_PIA_URL {ev.get('artist','')[:20]}\n"); continue
    cand = {'newid': i, 'artist': ev.get('artist', ''), 'urls': urls}
    try:
        ne = build(cand)
    except Exception as ex:
        out.append({'id': i, 'status': 'ERROR', 'artist': ev.get('artist', ''), 'err': str(ex)[:120]})
        sys.stderr.write(f"  {i} ERROR {ex}\n"); continue
    if ne is None:
        out.append({'id': i, 'status': 'delete', 'artist': ev.get('artist', ''),
                    'venue': ev.get('venue', ''), 'urls': cand['urls']})
        sys.stderr.write(f"  {i} DELETE {ev.get('artist','')[:20]}\n")
    else:
        out.append({'id': i, 'status': 'convert', 'artist': ev.get('artist', ''),
                    'tickets': ne['tickets'], 'date': ne['date'], 'dateLabel': ne['dateLabel'],
                    'venue': ne['venue'], 'prefecture': ne['prefecture']})
        sys.stderr.write(f"  {i} convert {len(ne['tickets'])}枠\n")

json.dump(out, open('tmp/convert_0710.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
nc = sum(1 for o in out if o['status'] == 'convert')
nd = sum(1 for o in out if o['status'] == 'delete')
sys.stderr.write(f"\n=== convert {nc} / delete {nd} ===\n")
if bpe._DROPPED:
    sys.stderr.write(f"!! DROPPED {len(bpe._DROPPED)}: {bpe._DROPPED}\n")
