# -*- coding: utf-8 -*-
"""id8000 斉藤由貴に東京9/25の枠を足したので、県・会期ラベル・会場を組み直したビルド結果（ぴあ実ページ）に合わせる。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
b = json.load(io.open('tmp/built_8000_0911.json', encoding='utf-8-sig'))[0]
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
ev = json.loads(m.group(2))
for e in ev:
    if e['id'] == 8000:
        for k in ('prefecture', 'dateLabel', 'venue', 'date'):
            print(k, ':', e.get(k), '→', b.get(k))
            e[k] = b.get(k)
open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + json.dumps(ev, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
