# -*- coding: utf-8 -*-
"""id5675 神韻日本公演2027 に山梨3/25〜・宮城3/30〜・静岡4/3〜を足したので、会期の初日を事実（山梨 2027/3/25）に合わせる。
会場名は神韻の組み直し結果（ぴあ実ページ）の venue を使う。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
b = [e for e in json.load(io.open('tmp/built_missF_0911.json', encoding='utf-8-sig')) if e['id'] == 9201][0]
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
ev = json.loads(m.group(2))
for e in ev:
    if e['id'] == 5675:
        old = e['dateLabel']
        e['dateLabel'] = re.sub(r'^2027年4月7日\(水\)', '2027年3月25日(木)', old)
        e['venue'] = b['venue']
        print(old, '→', e['dateLabel'])
        print(e['venue'])
open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + json.dumps(ev, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
