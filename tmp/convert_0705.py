# -*- coding: utf-8 -*-
"""7/5 期限切れ→販売中 変換 (構築側)。build_pia_entries.build()で各対象を現在の
買える枠で再構築。買える枠ゼロ(None)=売切/終了=削除候補。tmp/convert_0705.json出力。
対象=check_expired ⚠️要再確認155件 を機械再パース（7/4発売フリップ分の実終了日取り直し）。"""
import sys, json, re
sys.path.insert(0, 'tools')
import build_pia_entries as bpe
from build_pia_entries import build

IDS = [5,47,97,249,339,376,413,504,510,526,530,532,537,539,546,623,663,672,684,685,
       688,702,710,715,716,718,721,723,724,728,747,750,751,752,804,822,830,839,902,
       903,915,935,948,1094,1095,1096,1097,1098,1099,1100,1102,1103,1104,1105,1106,
       1107,1108,1109,1110,1111,1112,1114,1115,1116,1125,1148,1152,1177,1180,1184,
       1186,1195,1202,1209,1230,1237,1268,1274,1278,1288,1302,1312,1328,1360,1363,
       1382,1398,1430,1433,1582,1615,1617,1630,1641,1697,1718,1732,1740,1741,1742,
       1743,1744,1745,1746,1759,1760,1761,1762,1763,1764,1765,1766,1767,1769,1770,
       1771,1773,1774,1775,1776,1777,1778,1779,1780,1781,1783,1786,1788,1789,1790,
       1791,1793,1794,1809,1817,1818,1819,1820,1870,1871,1872,1873,1874,1875,1876,
       1877,1878,1879,1880,1881,1882,1883,1884,1885]

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

json.dump(out, open('tmp/convert_0705.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
nc = sum(1 for o in out if o['status'] == 'convert')
nd = sum(1 for o in out if o['status'] == 'delete')
sys.stderr.write(f"\n=== convert {nc} / delete {nd} ===\n")
if bpe._DROPPED:
    sys.stderr.write(f"!! DROPPED {len(bpe._DROPPED)}: {bpe._DROPPED}\n")
