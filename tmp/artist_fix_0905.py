# -*- coding: utf-8 -*-
"""独立検証で出た artist 欄の直し2件（2026-09-05）。

1) id6939「MEME× tzkwym 「血湧き肉躍る-ハロウィン-」」
   e+の登録ワードは「L-MEME/MEME エルメメ メメ」と「tzkwym ツヅキヲヨム」の2組。
   既存は id6022=L-MEME / id6207=L-MEME / tzkwym なので、「L-MEME」で探して出てこない状態だった。
   根拠 https://eplus.jp/sf/detail/4590340001-P0030001P021001
2) id6080 は artist が name とまったく同じ（イベント名まるごと）＝出演者名で探せない。
   実ページの出演は 東京キューバンボーイズ／アロージャズオーケストラ／渡辺真知子。
   同じ楽団が id6295 では artist=アロージャズオーケストラ で入っているので、片方だけ検索から漏れていた。
   根拠 https://eplus.jp/sf/detail/3666570001-P0030004P021001

🚨 index.html は newline='' で読み書き＋json.dumps の改行を元の改行コードへ置換（CRLFを壊さない）。
"""
import json, re, io, datetime

PATH = 'index.html'
TODAY = datetime.date.today().isoformat()

h = io.open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
assert m, 'EVENTS not found'
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
log = []

e = by[6939]
assert 'MEME' in e['artist'], e['artist']
e['artist'] = 'L-MEME／tzkwym'
e['verifiedAt'] = TODAY
log.append('id6939 artist -> L-MEME / tzkwym')

e = by[6080]
assert e['artist'] == e['name'], (e['artist'], e['name'])
e['artist'] = '東京キューバンボーイズ／アロージャズオーケストラ／渡辺真知子'
e['verifiedAt'] = TODAY
log.append('id6080 artist -> tokyo cuban boys / arrow jazz / watanabe machiko')

bak = 'index.html.bak_0905_artistfix'
io.open(bak, 'w', encoding='utf-8', newline='').write(h)
NL = '\r\n' if '\r\n' in h else '\n'
arr = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', NL)
io.open(PATH, 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + arr + m.group(3) + h[m.end():])
print('\n'.join(log))
print('backup=%s' % bak)
