# -*- coding: utf-8 -*-
"""6/29 期限切れ→販売中 変換 (構築側)。
build_pia_entries.build() を各対象エントリのぴあURL群で呼び、現在の買える枠で
tickets を作り直す。買える枠ゼロ(build が None)= 売切/終了確定 → 削除候補。
出力 tmp/convert_0629.json を後段 apply_0629.py が読んで index.html に適用する。
独立検証は reconcile_pia.py --ids (別実行) と突合する二段構え。"""
import sys, json, re
sys.path.insert(0, 'tools')
import build_pia_entries as bpe          # import時に sys.stdout をUTF-8ラップ
from build_pia_entries import build

IDS = [115,125,292,316,474,577,607,695,700,712,820,835,848,918,931,1037,1038,
       1039,1040,1041,1042,1043,1135,1146,1168,1189,1194,1228,1249,1250,1256,
       1258,1266,1271,1275,1279,1286,1393,1396,1399,1403,1406,1408,1415,1421,
       1422,1424,1425,1434,1437,1439,1442,1461,1469,1471,1476,1498,1499,1505,
       1510,1512,1513,1515,1536,1538,1540]

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
m = re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S)
EVENTS = json.loads(m.group(1))
byid = {e['id']: e for e in EVENTS}

out = []
for i in IDS:
    ev = byid.get(i)
    if not ev:
        out.append({'id': i, 'status': 'MISSING_IN_DB'}); continue
    urls = pia_urls(ev)
    cand = {'newid': i, 'artist': ev.get('artist', ''), 'urls': urls}
    try:
        ne = build(cand)
    except Exception as ex:
        out.append({'id': i, 'status': 'ERROR', 'artist': ev.get('artist', ''),
                    'err': str(ex)[:120], 'urls': urls})
        sys.stderr.write(f"  {i} ERROR {ex}\n"); continue
    if ne is None:
        out.append({'id': i, 'status': 'delete', 'artist': ev.get('artist', ''),
                    'venue': ev.get('venue', ''), 'date': ev.get('date', ''),
                    'urls': urls})
        sys.stderr.write(f"  {i} DELETE(売切/終了) {ev.get('artist','')[:24]}\n")
    else:
        out.append({'id': i, 'status': 'convert', 'artist': ev.get('artist', ''),
                    'tickets': ne['tickets'], 'date': ne['date'],
                    'dateLabel': ne['dateLabel'], 'venue': ne['venue'],
                    'prefecture': ne['prefecture'],
                    'old_tickets': ev.get('tickets', [])})
        sys.stderr.write(f"  {i} convert {len(ne['tickets'])}枠 {ev.get('artist','')[:24]}\n")

json.dump(out, open('tmp/convert_0629.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
nc = sum(1 for o in out if o['status'] == 'convert')
nd = sum(1 for o in out if o['status'] == 'delete')
ne_ = sum(1 for o in out if o['status'] in ('ERROR', 'MISSING_IN_DB'))
sys.stderr.write(f"\n=== convert {nc} / delete {nd} / error {ne_} ===\n")
if bpe._DROPPED:
    sys.stderr.write(f"!! DROPPED(取りこぼし) {len(bpe._DROPPED)}: {bpe._DROPPED}\n")
