# -*- coding: utf-8 -*-
"""バッジ0の救済①＝reconcile が MISSING を出したエントリの候補JSONを作る。
🚨そのエントリに紐づく**ぴあURLを全部**渡す（links.pia ＋ 全 ticket.url）。
   1本だけ渡すと build 側が multi=False にして ticket.url を刻まない
   （memory: feedback_build_pia_multiurl_loses_ticket_url）。"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

IDS = [1593, 2206, 2743, 2864, 3474, 3489, 3682, 4039, 4042, 4068, 4084, 4085, 4088,
       4100, 4329, 4374, 4385, 4389, 4390, 4393, 4394, 4397, 4401, 4402, 4406, 4409,
       4411, 4413, 4416, 4420, 4422, 4436, 4812, 4820, 4868, 4951, 4957, 4960, 5193]

src = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', src, re.S).group(1))
byid = {e['id']: e for e in EVENTS}

cands = []
for i in IDS:
    e = byid.get(i)
    if not e:
        print(f'  !! id{i} が見つからない'); continue
    urls = [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets', [])]
    urls = list(dict.fromkeys(u for u in urls if u and 't.pia.jp' in u))
    if not urls:
        print(f'  △ id{i} {e.get("artist")}: ぴあURLなし → 対象外'); continue
    cands.append({'newid': i, 'artist': e.get('artist'), 'urls': urls})

json.dump(cands, open('tmp/_zb_cand_0901.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'候補 {len(cands)}件 / URL合計 {sum(len(c["urls"]) for c in cands)}本 → tmp/_zb_cand_0901.json')
