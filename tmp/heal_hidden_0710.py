# -*- coding: utf-8 -*-
"""7/10 恒久ヒール: startDate==date（販売終了日 未取込）の枠を持つ全エントリを
ぴあ機械再パースし、正しい締切を取り込む。
 - date<today  : renderCard 49011行で非表示化＝買えるのに見えない子（96件）
 - date==today : 本日発売（発売時刻後に「本日発売」表示のまま締切不明）
出力 tmp/heal_hidden_0710.json  (status=convert/delete/NO_PIA_URL/ERROR)
"""
import sys, json, re, time
sys.path.insert(0, 'tools')
import build_pia_entries as bpe
from build_pia_entries import build

TODAY = '2026-07-10'

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

targets = []
for e in EVENTS:
    for t in e.get('tickets', []):
        sd = t.get('startDate'); d = t.get('date')
        if sd and sd == d and d <= TODAY and not t.get('saleUntilSoldOut'):
            targets.append(e); break

sys.stderr.write(f"対象 {len(targets)} エントリ\n")
out = []
for n, ev in enumerate(targets, 1):
    i = ev['id']
    urls = pia_urls(ev)
    if not urls:
        out.append({'id': i, 'status': 'NO_PIA_URL', 'artist': ev.get('artist', '')})
        sys.stderr.write(f"[{n}/{len(targets)}] {i} NO_PIA_URL\n"); continue
    cand = {'newid': i, 'artist': ev.get('artist', ''), 'urls': urls}
    try:
        ne = build(cand)
    except Exception as ex:
        out.append({'id': i, 'status': 'ERROR', 'artist': ev.get('artist', ''), 'err': str(ex)[:120]})
        sys.stderr.write(f"[{n}/{len(targets)}] {i} ERROR {str(ex)[:60]}\n")
        time.sleep(2.0); continue
    if ne is None:
        out.append({'id': i, 'status': 'delete', 'artist': ev.get('artist', ''),
                    'venue': ev.get('venue', ''), 'urls': urls})
        sys.stderr.write(f"[{n}/{len(targets)}] {i} DELETE\n")
    else:
        out.append({'id': i, 'status': 'convert', 'artist': ev.get('artist', ''),
                    'tickets': ne['tickets'], 'date': ne['date'], 'dateLabel': ne['dateLabel'],
                    'venue': ne['venue'], 'prefecture': ne['prefecture']})
        sys.stderr.write(f"[{n}/{len(targets)}] {i} convert {len(ne['tickets'])}枠\n")
    time.sleep(1.2)

json.dump(out, open('tmp/heal_hidden_0710.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
nc = sum(1 for o in out if o['status'] == 'convert')
nd = sum(1 for o in out if o['status'] == 'delete')
ne_ = sum(1 for o in out if o['status'] == 'ERROR')
sys.stderr.write(f"\n=== convert {nc} / delete {nd} / ERROR {ne_} ===\n")
if bpe._DROPPED:
    sys.stderr.write(f"!! DROPPED {len(bpe._DROPPED)}\n")
