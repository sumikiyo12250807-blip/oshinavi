# -*- coding: utf-8 -*-
"""id3568 に、ぴあの「一般発売（静岡 12/11公演）9/19 10:00発売」を足す（reconcile_pia の MISSING）。
登録済みはローチケの同じ枠だけ＝飛び先が違うので畳まずに並べる（feedback_dedup_badges_keeps_urls）。"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
ev = json.loads(m.group(2))
PIA = 'https://t.pia.jp/pia/event/event.do?eventCd=2606894'
for e in ev:
    if e['id'] != 3568:
        continue
    if any(t.get('url') == PIA and t.get('startDate') == '2026-09-19' for t in e['tickets']):
        print('既にある'); break
    i = next(k for k, t in enumerate(e['tickets']) if t['type'] == '一般発売（静岡 12/11公演）9/19 10:00発売')
    e['tickets'].insert(i, {'type': '一般発売（静岡 12/11公演）9/19 10:00発売', 'startDate': '2026-09-19',
                            'date': '2026-09-19', 'url': PIA})
    print('足した:', len(e['tickets']), '枠')
open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + json.dumps(ev, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
