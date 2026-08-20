# -*- coding: utf-8 -*-
"""重複の相手（既存3239 大阪芸術花火 / 既存1768 ナーポオケラ）と、新着側の枠を並べて出す。
既存に無い枠があれば既存へ移植する（[[feedback_harvest_dedup_check]] の手順4）。"""
import json
import re

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}
new = {e['id']: e for e in json.load(open('tmp/new50_0730.json', encoding='utf-8'))}

PAIRS = [(3239, 3516), (1768, 3517)]
out = []
for oldid, newid in PAIRS:
    o, n = byid.get(oldid), new.get(newid)
    out.append(f'===== 既存 id={oldid} =====')
    out.append(f"  artist={o.get('artist')}")
    out.append(f"  venue={o.get('venue')}  date={o.get('date')}  dateLabel={o.get('dateLabel')}")
    out.append(f"  genre={o.get('genre')}  links.rakuten={(o.get('links') or {}).get('rakuten')}")
    for t in o.get('tickets') or []:
        out.append(f"    枠: {t.get('type')}  [date={t.get('date')} start={t.get('startDate')}]")
    out.append(f'----- 新着 id={newid}（今回作った方） -----')
    out.append(f"  artist={n.get('artist')}")
    out.append(f"  venue={n.get('venue')}  date={n.get('date')}")
    for t in n.get('tickets') or []:
        out.append(f"    枠: {t.get('type')}  [date={t.get('date')} start={t.get('startDate')}]")
    out.append('')
open('tmp/peek_dup_targets_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/peek_dup_targets_0730.txt')
