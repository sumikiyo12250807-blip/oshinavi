# -*- coding: utf-8 -*-
"""id=1 さだまさし: 山梨(8/23)・静岡(8/25)枠を落とす。
根拠= 楽天ツアーページ「取り扱いなし」/ ぴあ アーティストページ(artistsCd=11010822)の
販売中・発売前一覧に山梨・静岡が出ない = 両プレイガイドで買えない。
兵庫・京都(8/17-19・予定枚数終了まで・楽天)は生存のためエントリは維持。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
for e in EVENTS:
    if e['id'] != 1: continue
    e['tickets'] = [t for t in e['tickets'] if '山梨・静岡' not in (t.get('type') or '')]
    e['date'] = '2026-08-19'
    e['dateLabel'] = '2026年8月17日(月)兵庫／19日(水)京都'
    e['venue'] = '神戸国際会館こくさいホール／ロームシアター京都メインホール'
    e['prefecture'] = '兵庫・京都'
    e['verifiedAt'] = '2026-07-10'
    print(json.dumps(e, ensure_ascii=False, indent=1))
if DRY:
    print("(DRY)")
else:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0710_fix1_sada','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():])
    print("written")
