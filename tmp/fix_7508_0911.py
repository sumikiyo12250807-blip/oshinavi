# -*- coding: utf-8 -*-
"""id7508 あつこ&タニケン に同じツアー（ハッピードレミハウス）の宮城・愛知を足したので、
会期と会場をツアーの事実に合わせる（[[feedback_show_true_dates_not_sellable_range]]）。
会期と会場はビルド結果（ぴあのツアーまとめ b2671021 の実ページ）から写す。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
b = {e['id']: e for e in json.load(io.open('tmp/built_0911_fresh.json', encoding='utf-8-sig'))}[7841]
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
ev = json.loads(m.group(2))
for e in ev:
    if e['id'] == 7508:
        print('前:', e['dateLabel'], '|', e['venue'], '|', e['prefecture'], '|', e['date'])
        e['dateLabel'] = b['dateLabel']
        e['venue'] = b['venue']
        e['prefecture'] = b['prefecture']
        e['date'] = b['date']
        print('後:', e['dateLabel'], '|', e['venue'], '|', e['prefecture'], '|', e['date'])
open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + json.dumps(ev, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
