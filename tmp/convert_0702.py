# -*- coding: utf-8 -*-
"""7/2 期限切れ→販売中 変換 (構築側)。build_pia_entries.build()で各対象を現在の
買える枠で再構築。買える枠ゼロ(None)=売切/終了=削除候補。tmp/convert_0702.json出力。
※id6=楽天/id80=e+ はぴあ非対応なので別途WebFetch(このスクリプトはpia分のみ)。"""
import sys, json, re
sys.path.insert(0, 'tools')
import build_pia_entries as bpe
from build_pia_entries import build

# check_expired.py (today=2026-07-02) が挙げた⚠️要再確認40件から pia分38件
# (id6=楽天/id80=e+ は除外し個別WebFetch)
IDS = [800,859,876,896,923,1049,1050,1052,1053,1054,1155,1162,1197,1198,1213,1228,
       1244,1260,1264,1315,1316,1318,1322,1327,1368,1371,1376,1378,1381,1397,1405,
       1417,1438,1541,1604,1638,1646,1647]

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
    cand = {'newid': i, 'artist': ev.get('artist', ''), 'urls': pia_urls(ev)}
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

json.dump(out, open('tmp/convert_0702.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
nc = sum(1 for o in out if o['status'] == 'convert')
nd = sum(1 for o in out if o['status'] == 'delete')
sys.stderr.write(f"\n=== convert {nc} / delete {nd} ===\n")
if bpe._DROPPED:
    sys.stderr.write(f"!! DROPPED {len(bpe._DROPPED)}: {bpe._DROPPED}\n")
