# -*- coding: utf-8 -*-
"""id7813 FEST. INAZUMA 2026 の枠に「販売終了」の印を付ける（2026-09-11 ユーザー選択「1で」＝消さずに販売終了で公演日まで出す）。
根拠＝ぴあの実ページ「現在販売中のチケット情報はありません」・プリセール/一般とも「販売終了」（9/11朝の独立再導出）。
DELETE_GATE 1章＝販売終了は soldout:true ＋ saleEnded:true ＋ saleEndedSince。"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
ev = json.loads(m.group(2))
for e in ev:
    if e['id'] == 7813:
        for t in e['tickets']:
            t['soldout'] = True
            t['saleEnded'] = True
            t['saleEndedSince'] = t.get('date') or '2026-09-10'
            print(t)
open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + json.dumps(ev, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
