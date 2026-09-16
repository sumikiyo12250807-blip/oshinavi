# -*- coding: utf-8 -*-
"""id6239 未唯mie にぴあの枠を足したら県が「東京都・東京」と二重になり、日付ラベルから会場名が落ちた。
e+表記（東京都）とぴあ表記（東京）が混ざっただけなので、1つにそろえてぴあのリンクも付ける。"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
ev = json.loads(m.group(2))
for e in ev:
    if e['id'] == 6239:
        e['prefecture'] = '東京'
        e['dateLabel'] = '2026年9月19日(土) 東京 東京国際フォーラム ホールC'
        e.setdefault('links', {})['pia'] = 'https://t.pia.jp/pia/event/event.do?eventCd=2609282'
        print(e['prefecture'], '|', e['dateLabel'], '|', e['links'])
open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + json.dumps(ev, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
