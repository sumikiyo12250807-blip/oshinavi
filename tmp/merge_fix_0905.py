# -*- coding: utf-8 -*-
"""e+の実ページ照合で分かった既存エントリの直し（2026-09-05・夜の追加ぶん）。

1) id6103 川崎学園祭 お笑いライブ!!（岡山 10/18）
   e+ 4573500001 に同じ公演。受付 2026/9/6 10:00〜2026/10/17 → 締切が発売日のままだったので直す＋URL＋出演者
2) id6295 アロージャズオーケストラ（奈良 12/5 たけまるホール）
   e+ 0314250001-P0030050：先着一般発売 9/19 10:00〜11/27 の枠が丸ごと抜けていた → 追加
3) id6080 灼熱のマンボVS輝けるスイング!（愛知 R9年 1/13）
   e+ 3666570001-P0030004：一般発売 9/19 10:00〜2027/1/9 → 締切を直す＋URL
4) id583 MELANCHOLIC CIRCUS に「サーカス」（加藤実）の東京12/2枠が2つ混入していた。
   ぴあ eventCd=2630866 のページ表題は「サーカス」＝部分一致で畳んだ事故。
   → 2枠を外し、愛知9/26の単独公演に戻す。外した公演は新規エントリ（サーカス／加藤実）として新着に入れる。

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

# --- 1) id6103 -------------------------------------------------------------
e = by[6103]
assert len(e['tickets']) == 1, e['tickets']
t = e['tickets'][0]
assert t['date'] == '2026-09-06', t
t['date'] = '2026-10-17'
t['url'] = 'https://eplus.jp/sf/detail/4573500001-P0030001P021001'
e['artist'] = '三四郎／ティモンディ／ぱーてぃーちゃん'
e.setdefault('links', {})['eplus'] = 'https://eplus.jp/sf/detail/4573500001-P0030001P021001'
e['verified'] = True
e['verifiedAt'] = TODAY
log.append('id6103 kawasaki-gakusai: end 9/6->10/17, url, performers')

# --- 2) id6295 -------------------------------------------------------------
e = by[6295]
assert e['date'] == '2026-12-05', e['date']
urls = [t.get('url') for t in e['tickets']]
assert 'https://eplus.jp/sf/detail/0314250001-P0030050P021001' not in urls
e['tickets'].append({
    'type': '先着一般発売（奈良 12/5公演）9/19 10:00発売',
    'date': '2026-11-27',
    'startDate': '2026-09-19',
    'url': 'https://eplus.jp/sf/detail/0314250001-P0030050P021001',
})
e['name'] = 'アロージャズオーケストラ クリスマスジャズ&ポピュラーコンサート ゲスト:サーカス'
e.setdefault('links', {})['eplus'] = 'https://eplus.jp/sf/detail/0314250001-P0030050P021001'
e['verified'] = True
e['verifiedAt'] = TODAY
log.append('id6295 arrow-jazz: added ippan slot (slots=%d)' % len(e['tickets']))

# --- 3) id6080 -------------------------------------------------------------
e = by[6080]
assert len(e['tickets']) == 1, e['tickets']
t = e['tickets'][0]
assert t['date'] == '2026-09-19', t
t['date'] = '2027-01-09'
t['url'] = 'https://eplus.jp/sf/detail/3666570001-P0030004P021001'
e.setdefault('links', {})['eplus'] = 'https://eplus.jp/sf/detail/3666570001-P0030004P021001'
e['verified'] = True
e['verifiedAt'] = TODAY
log.append('id6080 mambo-vs-swing: end 9/19->2027-01-09, url')

# --- 4) id583 --------------------------------------------------------------
e = by[583]
before = len(e['tickets'])
e['tickets'] = [t for t in e['tickets'] if '2630866' not in (t.get('url') or '')]
assert before - len(e['tickets']) == 2, (before, len(e['tickets']))
e['date'] = '2026-09-26'
e['dateLabel'] = '2026年9月26日(土) 愛知 池下CLUB UPSET'
e['venue'] = '池下CLUB UPSET'
e['prefecture'] = '愛知'
e['verified'] = True
e['verifiedAt'] = TODAY
log.append('id583 melancholic-circus: removed 2 circus slots, back to aichi 9/26')

bak = 'index.html.bak_0905_mergefix'
io.open(bak, 'w', encoding='utf-8', newline='').write(h)
NL = '\r\n' if '\r\n' in h else '\n'
arr = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', NL)
body = h[:m.start()] + m.group(1) + arr + m.group(3) + h[m.end():]
io.open(PATH, 'w', encoding='utf-8', newline='').write(body)
print('\n'.join(log))
print('backup=%s' % bak)
