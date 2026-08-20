# -*- coding: utf-8 -*-
"""7/4 期限切れ→販売中 変換 (構築側)。build_pia_entries.build()で各対象を現在の
買える枠で再構築。買える枠ゼロ(None)=売切/終了=削除候補。tmp/convert_0704.json出力。
対象=check_expired ⚠️要再確認48件 + 公演終了扱いの3件(81/115/570)を機械再パース。"""
import sys, json, re
sys.path.insert(0, 'tools')
import build_pia_entries as bpe
from build_pia_entries import build

IDS = [81, 115, 570,
       82,106,253,255,306,312,531,556,614,699,737,852,1083,1084,1085,1086,
       1092,1093,1176,1235,1302,1309,1316,1349,1398,1491,1529,1628,1689,
       1709,1710,1711,1712,1713,1714,1715,1717,1719,1720,1723,1725,1726,
       1727,1728,1731,1758,1812,1816]

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
        out.append({'id': i, 'status': 'NO_PIA_URL', 'artist': ev.get('artist', ''),
                    'venue': ev.get('venue', '')})
        sys.stderr.write(f"  {i} NO_PIA_URL (eplus等) {ev.get('artist','')[:20]}\n"); continue
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

json.dump(out, open('tmp/convert_0704.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
nc = sum(1 for o in out if o['status'] == 'convert')
nd = sum(1 for o in out if o['status'] == 'delete')
sys.stderr.write(f"\n=== convert {nc} / delete {nd} ===\n")
if bpe._DROPPED:
    sys.stderr.write(f"!! DROPPED {len(bpe._DROPPED)}: {bpe._DROPPED}\n")
