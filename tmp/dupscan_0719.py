# -*- coding: utf-8 -*-
"""DB全件の重複スキャン。会場＋公演日の一致で「表記違いの二重登録」を洗う。
（eventCd/名前の完全一致では大西宇宙（Br）⇔大西宇宙 バリトン・リサイタル がすり抜けた）
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))
print('全', len(E), '件\n')

def cds(e):
    s = set()
    urls = [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets', [])]
    for u in urls:
        if u:
            s |= set(re.findall(r'event(?:Bundle)?Cd=([A-Za-z0-9]+)', u))
    return s

g = {}
for e in E:
    v, d = e.get('venue'), e.get('date')
    if not v or not d:
        continue
    # 全国ツアーは会場がまとめ表記になるので除外（別ツアー同士が偶然当たる）
    if '全国ツアー' in v or 'ほか' in v:
        continue
    g.setdefault((v, d), []).append(e)

n = 0
for (v, d), lst in sorted(g.items(), key=lambda x: x[0][1]):
    if len(lst) < 2:
        continue
    # eventCd が完全に別 かつ 名前も完全一致でない → 目視対象
    n += 1
    print(f'■ {v} / {d}')
    for e in lst:
        print(f'   id={e["id"]} [{e.get("genre")}] {e.get("name")}')
        print(f'      枠{len(e.get("tickets", []))} cd={sorted(cds(e))}')
    print()

print(f'=== 会場＋公演日が重なる組 {n} 件 ===')
