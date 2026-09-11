# -*- coding: utf-8 -*-
"""id3568 GENERATIONS LIVE TOUR 2026 "PARALLEL QUEST" のカードを事実に合わせる。
- 会期＝公式（ldh-liveschedule.jp/sys/tour/40102/）の全12公演＝10/31(土) 長野〜12/23(水) 代々木
- 会場一覧＝公式の8会場
- 「9次プレリザーブ（福岡 11/3公演）」に福岡のぴあURL（eventCd=2606881・ぴあ総ざらいで確認）を焼き込む
  （url が空だとカードのリンク＝静岡のぴあページへ飛ぶ）
CRLF を保つため、テキストモードで読み書きする。"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
ev = json.loads(m.group(2))
hit = 0
for e in ev:
    if e['id'] != 3568:
        continue
    hit += 1
    print('前:', e['date'], e['dateLabel'], e['venue'])
    e['date'] = '2026-12-23'
    e['dateLabel'] = '2026年10月31日(土)〜2026年12月23日(水) 全国ツアー'
    e['venue'] = ('全国ツアー（長野ビッグハット／マリンメッセ福岡 A館／有明アリーナ／サンドーム福井／'
                  '大阪城ホール／ワールド記念ホール／エコパアリーナ／国立代々木競技場 第一体育館）')
    for t in e['tickets']:
        if t['type'].startswith('9次プレリザーブ（福岡 11/3公演）') and not t.get('url'):
            t['url'] = 'https://t.pia.jp/pia/event/event.do?eventCd=2606881'
            print('福岡の枠にURL:', t['type'])
    print('後:', e['date'], e['dateLabel'], e['venue'])
assert hit == 1
open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + json.dumps(ev, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
