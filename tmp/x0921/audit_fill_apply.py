# -*- coding: utf-8 -*-
"""取りこぼし24件のうち、ぴあで買える枠があった6件を index.html に入れる（2026-09-21）。
  足し込み: 950016 新しい学校のリーダーズ Zepp Fukuoka 11/27 → id6094（全国ツアーのエントリ・福岡の枠が無かった）
  新規    : 950012 ドリフェス / 950013 FUKUOKA MUSIC FES / 950017 推し選寄席 / 950021 TOMIHAMA FES / 950023 BEEEEM FES
  TOMIHAMA は駐車券の枠を外し（出す側・駐車券だけは載せない）、会場を「富浜緑地」に直す。
残り18件はぴあで全カードが予定枚数終了／販売終了／抽選受付終了＝買える枠0で入れない。
読み書きは inject_built.py と同じ（newline='' で CRLF を保つ）。
使い方: python tmp/x0921/audit_fill_apply.py [--apply]
"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
built = {e['id']: e for e in json.load(io.open('tmp/x0921/audit_fill_built.json', encoding='utf-8'))}
h = io.open(P, encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))
by = {e['id']: e for e in EV}

# --- 足し込み ---
src = built[950016]
dst = by[6094]
assert dst['artist'] == '新しい学校のリーダーズ'
have = {(t.get('type'), t.get('url')) for t in dst['tickets']}
for t in src['tickets']:
    t = dict(t)
    t.setdefault('url', src['links']['pia'])   # 1URL由来は ticket.url が付かない＝飛び先を焼き込む
    assert (t['type'], t['url']) not in have
    dst['tickets'].append(t)
    print('足し込み id6094 +', t['type'], t['url'])

# --- 新規 ---
nid = max(e['id'] for e in EV) + 1
new = []
for k in (950012, 950013, 950017, 950021, 950023):
    e = json.loads(json.dumps(built[k]))
    if k == 950021:
        e['tickets'] = [t for t in e['tickets'] if '駐車' not in t['type']]
        e['venue'] = '富浜緑地'
        e['dateLabel'] = '2026年11月14日(土)〜2026年11月15日(日) 愛知 富浜緑地'
    assert e['tickets'], k
    e['id'] = nid; nid += 1
    assert e['genre'] == 'new'
    new.append(e)
    print('新規 id%d %s 枠%d' % (e['id'], e['name'][:40], len(e['tickets'])))
EV.extend(new)
ids = [e['id'] for e in new]

if '--apply' not in sys.argv:
    print('(--apply で書き込み)'); sys.exit(0)

mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
merged = cur + [i for i in ids if i not in cur]
h2, n = re.subn(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', lambda mm: mm.group(1) + '[' + ', '.join(map(str, merged)) + ']', h, count=1)
assert n == 1
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)
arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\n', NL)
io.open(P, 'w', encoding='utf-8', newline='').write(h2[:m.start()] + m.group(1) + arr + m.group(3) + h2[m.end():])
print('書き込み完了 新規ids=%s NEW_ORDER %d→%d' % (ids, len(cur), len(merged)))
