# -*- coding: utf-8 -*-
"""ローチケ9件のジャンル下書きの手がかり＝同じアーティストが既にOSHINAVIで入っているジャンル（読むだけ）。"""
import collections, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
KEYS = {7819: ['環ROY', 'ぷにぷに電機', 'Bucket Drummer', 'SUPERNOVA KAWASAKI'], 7820: ['別府葉子'], 7821: ['野田かつひこ'],
        7822: ['櫻坂46'], 7823: ['HAPPINESS JAM', '新しい学校のリーダーズ', '水曜日のカンパネラ'], 7824: ['東京キューバンボーイズ', '見砂和照'],
        7825: ['岩崎宏美', '国府弘子'], 7826: ['星波'], 7827: ['歌声コンサート']}
src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
for i, ks in KEYS.items():
    c = collections.Counter()
    for e in ev:
        if e['id'] == i or e.get('genre') == 'new':
            continue
        hay = (e.get('artist') or '') + ' ' + (e.get('name') or '')
        for k in ks:
            if k in hay:
                c['%s:%s' % (k, e.get('genre'))] += 1
    print('id%s %s' % (i, dict(c) or '（手がかりなし）'))
