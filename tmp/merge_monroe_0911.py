# -*- coding: utf-8 -*-
"""MICHAEL MONROE 名古屋(eventCd=2636782)の枠に飛び先を焼き込み、既存 id7726（梅田）へ足す候補にする。"""
import io, json
b = json.load(io.open('tmp/built_monroe_0911.json', encoding='utf-8-sig'))
u = 'https://t.pia.jp/pia/event/event.do?eventCd=2636782'
for e in b:
    for t in e['tickets']:
        t['url'] = t.get('url') or u
json.dump(b, io.open('tmp/built_monroe_0911.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('ok', len(b[0]['tickets']))
