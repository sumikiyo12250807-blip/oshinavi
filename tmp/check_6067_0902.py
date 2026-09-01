# -*- coding: utf-8 -*-
"""id6067 の t5（締切ズレ FAIL）を実ページで確かめる。ツールの言い分を鵜呑みにしない。"""
import re, json, sys
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
from eplus_harvest import fetch, parse_ld

h = open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
e = next(x for x in EV if x['id'] == 6067)
print('id6067', e.get('artist'), '/ 公演日', e.get('date'), '/ 会場', e.get('venue'))
for i, t in enumerate(e.get('tickets') or []):
    print(f"  t{i} date={t.get('date')} start={t.get('startDate')} | {t.get('type')}")
    print(f"       {t.get('url')}")
url = (e['tickets'][5] or {}).get('url')
print('\n--- 実ページ', url)
html = fetch(url)
lds = parse_ld(html)
print('LD件数', len(lds))
for ld in lds:
    print(json.dumps(ld, ensure_ascii=False)[:600])
# 販売期間の窓を生HTMLから拾う
for m in re.finditer(r'(\d{4})[/年](\d{1,2})[/月](\d{1,2})日?\s*\(?[^\)]{0,3}\)?\s*(\d{1,2}):(\d{2})', html):
    pass
wins = re.findall(r'受付期間[^<]*<[^>]*>([^<]+)', html)
print('\n受付期間らしき文字列:', wins[:10])
