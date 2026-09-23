# -*- coding: utf-8 -*-
"""取りこぼし24件：足す先の既存エントリ候補を名前で探す（読むだけ）。"""
import io, json, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))
print('総件数', len(EV), '最大id', max(e['id'] for e in EV))
KEYS = ['YAMATO String', 'センダイガールズ', '仙女', '八神純子', '大阪プロレス', '東京スカパラ', 'ドリームフェスティバル',
        'FUKUOKA MUSIC FES', '反田恭平', '尾高忠明', '大阪フィル', '新しい学校のリーダーズ', '推し選寄席',
        'ドラゴンクエスト', 'ジョン・ウィリアムズ', 'TOKYO WIND', 'TOMIHAMA', '辻本玲', 'BEEEEM', '東京ウインド']
N = lambda s: unicodedata.normalize('NFKC', s or '')
for k in KEYS:
    hits = [e for e in EV if N(k) in N(e.get('artist')) or N(k) in N(e.get('name'))]
    print('##', k, len(hits))
    for e in hits[:12]:
        print('   id%s ｜%s ｜%s ｜genre=%s ｜枠%d ｜%s' % (e['id'], e.get('artist'), (e.get('name') or '')[:40], e.get('genre'),
              len(e.get('tickets') or []), e.get('date')))
