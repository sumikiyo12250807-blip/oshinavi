# -*- coding: utf-8 -*-
"""7/6 新着50件の枠取りこぼし総点検。各候補を今のぴあ状態でbuild()再構築し、
現登録のticketsと比較。ぴあ側に枠が増えてる(先行後付け等)エントリを検出。
出力 tmp/rescan_0706.json = [{id, cur_types, fresh_tickets, gained}]。"""
import sys, json, re
sys.path.insert(0, 'tools')
import build_pia_entries as bpe
from build_pia_entries import build

cands = json.load(open('tmp/cand_new_0706.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S).group(1))
byid = {e['id']: e for e in EVENTS}

def keyset(tickets):
    # (販売方法+発売日)で枠を識別。typeの県/公演表記ゆれを避けるためdate中心+type先頭語
    ks = set()
    for t in tickets or []:
        typ = (t.get('type', '') or '')
        head = re.split(r'（', typ)[0].strip()
        ks.add((head, t.get('date', ''), t.get('startDate', '')))
    return ks

out = []
for c in cands:
    i = c['newid']
    cur = byid.get(i)
    if not cur:
        continue
    try:
        fresh = build({'newid': i, 'artist': c['artist'], 'urls': c['urls']})
    except Exception as ex:
        out.append({'id': i, 'error': str(ex)[:100]}); continue
    if fresh is None:
        out.append({'id': i, 'fresh_none': True, 'cur_n': len(cur.get('tickets', []))}); continue
    cur_k = keyset(cur.get('tickets'))
    fresh_k = keyset(fresh['tickets'])
    gained = fresh_k - cur_k
    if gained:
        out.append({'id': i, 'artist': c['artist'][:30],
                    'cur_n': len(cur.get('tickets', [])), 'fresh_n': len(fresh['tickets']),
                    'gained': [list(g) for g in gained],
                    'fresh_tickets': fresh['tickets'], 'fresh_date': fresh['date']})

json.dump(out, open('tmp/rescan_0706.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
sys.stderr.write(f"=== 枠増加(要更新) {len(out)}件 ===\n")
for o in out:
    sys.stderr.write(f"  id{o['id']} {o.get('artist','')} {o.get('cur_n','?')}枠->{o.get('fresh_n','?')}枠 {o.get('error') or o.get('fresh_none','')}\n")
