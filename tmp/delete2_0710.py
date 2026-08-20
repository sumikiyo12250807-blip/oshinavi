# -*- coding: utf-8 -*-
"""7/10 追加削除5件（ユーザーOK「①削除OK」）。全件ぴあ実ページWebFetch裏取り済み。
 845  山川豊          今日10:00発売→予定枚数終了
 2144 真風涼帆 特別公演 今日10:00発売→予定枚数終了
 2304 柴田聡子        全枠 予定枚数終了/販売終了（ユーザー指摘）
 2308 Dos Monos      今日公演・当日券が今日21:00締切＝将来枠なし（ユーザー指摘）
 2314 Laughing Hick  今日公演・今日締切＝将来枠なし
"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DEL = {845, 2144, 2304, 2308, 2314}
DRY = '--apply' not in sys.argv
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
before = len(EVENTS)
kept = [e for e in EVENTS if e.get('id') not in DEL]
removed = [(e['id'], e.get('artist', '')) for e in EVENTS if e.get('id') in DEL]
for i, a in removed:
    print(f'  - {a}')
print(f"=== delete {len(removed)}/{len(DEL)} (before {before} -> after {len(kept)}) ===")
missing = DEL - {i for i, _ in removed}
if missing: print('!! not found:', sorted(missing))
# NEW_ORDER からも落とす
mo = re.search(r'const NEW_ORDER = \[([^\]]*)\];', h)
if DRY:
    print('(DRY)')
else:
    new_arr = json.dumps(kept, ensure_ascii=False, indent=2)
    out = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
    if mo:
        cur = [x.strip() for x in mo.group(1).split(',') if x.strip() and int(x.strip()) not in DEL]
        out = re.sub(r'(const NEW_ORDER = )\[[^\]]*\](;)', r'\g<1>[' + ', '.join(cur) + r']\2', out, count=1)
        print(f'NEW_ORDER {len(cur)}件')
    open('index.html.bak_0710_delete2','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(out)
    print('written (backup: index.html.bak_0710_delete2)')
