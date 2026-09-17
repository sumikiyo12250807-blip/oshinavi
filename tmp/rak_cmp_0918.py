# -*- coding: utf-8 -*-
# 楽天ハーベストの「発売前」「販売中」を、OSHINAVIの登録と突き合わせる
import json, io, re

d = json.load(open('tmp/rakuten_presale.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))

# 楽天スラッグ → 登録エントリ
slug_to_ids = {}
for e in ev:
    s = json.dumps(e, ensure_ascii=False)
    for m in re.finditer(r'(rt[0-9a-z]{5})', s):
        slug_to_ids.setdefault(m.group(1), set()).add(e['id'])

out = io.open('tmp/rak_cmp_0918.txt', 'w', encoding='utf-8')
for key, label in (('presale', '🎯これから発売'), ('onsale', '販売中')):
    rows = d[key]
    unreg = [r for r in rows if not slug_to_ids.get((re.search(r'/(rt[0-9a-z]{5})/', r['url']) or [None, ''])[1])]
    reg = [r for r in rows if r not in unreg]
    out.write(f"\n=== {label} {len(rows)}件（未登録 {len(unreg)} / 登録済 {len(reg)}）===\n")
    out.write('--- 未登録 ---\n')
    for r in unreg:
        w = ' / '.join(f"{x['type']} {x['timming']}" for x in (r.get('windows') or [])[:3])
        out.write(f"{r['name'][:44]}\t{r['first']}〜{r['last']}\t公演{r['perfs']}\t{r['_genre']}\n  {r['url']}\n  枠: {w}\n")
    out.write('--- 登録済（発売前の枠が抜けていないか見る）---\n')
    for r in reg:
        sl = (re.search(r'/(rt[0-9a-z]{5})/', r['url']) or [None, ''])[1]
        ids = sorted(slug_to_ids.get(sl, []))
        w = ' / '.join(f"{x['type']} {x['timming']}" for x in (r.get('windows') or [])[:3])
        out.write(f"id{ids}\t{r['name'][:40]}\t{r['first']}〜{r['last']}\n  枠: {w}\n")
out.close()
print('ok')
