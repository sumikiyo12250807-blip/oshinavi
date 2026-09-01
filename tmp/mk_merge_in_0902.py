# -*- coding: utf-8 -*-
"""統合の入力JSONを index.html から機械で作る。URLは絶対に手で書かない
（feedback_no_fabricated_output／eventCdの創作で2回事故）。

統合する2組（どちらも同じ演目が東京公演と大阪公演で2エントリに割れている）:
  6136 舞台「呪術廻戦」-渋谷事変前編-／東京  +  6137 ／大阪
  6105 劇団「ハイキュー!!」“勝者と敗者”／東京 +  6106 ／大阪
残す側のidに、両方のぴあURLを渡して再導出する（multi=True になり ticket.url が刻まれる）。
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

PAIRS = [(6136, 6137, '舞台「呪術廻戦」-渋谷事変前編-'),
         (6105, 6106, '劇団「ハイキュー!!」“勝者と敗者”')]

h = open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
by = {e['id']: e for e in EV}


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


cands = []
for keep, drop, name in PAIRS:
    urls = pia_urls(by[keep]) + [u for u in pia_urls(by[drop]) if u not in pia_urls(by[keep])]
    print(f'keep={keep} drop={drop} {name}')
    for u in urls:
        print('   ', u)
    cands.append({'newid': keep, 'artist': name, 'urls': urls})
json.dump(cands, open('tmp/merge_in_0902.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
print('\nwrote tmp/merge_in_0902.json')
