# -*- coding: utf-8 -*-
"""統合4組の入力JSONを機械で作る。URLは手で書かない。

  6290 TOMOVSKY               → 既存 695
  6332 「おとうさんといっしょ」レオてつコンサート → 既存 4223
  6343 エリザベート弦楽アンサンブル → 既存 2111
  6352 反田恭平&ザルツブルク…     → 既存 3406

既存のぴあURL＋新しく拾ったURLを**全部**渡す（1本だけ渡すと multi=False になって
ticket.url が刻まれない＝feedback_build_pia_multiurl_loses_ticket_url）。
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
PAIRS = [(695, 6290), (4223, 6332), (2111, 6343), (3406, 6352)]

h = open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
by = {e['id']: e for e in EV}
cand = {c['newid']: c for c in json.load(open('tmp/_newbuild_in_0902.json', encoding='utf-8'))}


def pia_urls(e):
    out = []
    u = (e.get('links') or {}).get('pia')
    if u:
        out.append(u)
    for t in (e.get('tickets') or []):
        tu = t.get('url') or ''
        if tu and 'pia.jp' in tu and tu not in out:
            out.append(tu)
    return out


rows = []
for keep, newid in PAIRS:
    e = by[keep]
    urls = pia_urls(e)
    for u in cand[newid]['urls']:
        if u not in urls:
            urls.append(u)
    print(f'keep={keep} {e.get("artist","")[:30]} ← new{newid}  URL{len(urls)}本')
    for u in urls:
        print('   ', u)
    rows.append({'newid': keep, 'artist': e.get('artist', ''), 'urls': urls})
json.dump(rows, open('tmp/merge2_in_0902.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\nwrote tmp/merge2_in_0902.json')
