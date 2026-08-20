# -*- coding: utf-8 -*-
"""トリオ|クリスマス 2026 の5件を id3303 に統合し、3304-3307 を消す。
   あわせて NEW_ORDER の二重配列 [[...]] を平らな [...] に直す
   （直前の統合スクリプトが group(2) の外側にも括弧を足してしまった自分のバグ）。
"""
import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = 'index.html'
apply = '--apply' in sys.argv
KEEP, DROP = 3303, [3304, 3305, 3306, 3307]

built = json.load(open('tmp/igarashi_trio.json', encoding='utf-8'))['built']
src = open(PATH, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by_id = {e['id']: e for e in events}

merged_urls = {t['url'] for t in built['tickets']}
for eid in [KEEP] + DROP:
    e = by_id[eid]
    assert e.get('genre') == 'new', f'id{eid} が新着でない'
    own = (e.get('links') or {}).get('pia')
    assert own in merged_urls, f'id{eid} のURL {own} が統合後の枠に無い'
    print(f'  id{eid} {e["name"][:44]} → 枠が統合先に存在 OK')
assert len(built['tickets']) == 5, '枠数が5でない'

k = by_id[KEEP]
for f in ('artist', 'name', 'date', 'dateLabel', 'venue', 'prefecture',
          'tickets', 'links', 'verifiedAt'):
    k[f] = built[f]
events = [e for e in events if e['id'] not in DROP]

print(f'\n統合後 id{KEEP}: {k["name"]}')
print(f'  venue: {k["venue"]}')
print(f'削除: {DROP}（欠番のまま残す）')

# --- NEW_ORDER: 括弧ごと丸ごと差し替える（入れ子も数字だけ拾うので平らになる） ---
mo = re.search(r'(const NEW_ORDER\s*=\s*)(\[[\[\]0-9,\s]*\])(\s*;)', src)
assert mo, 'NEW_ORDERが見つからない'
cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
nested = mo.group(2).lstrip().startswith('[[')
new_order = [i for i in cur if i not in DROP]
print(f'\nNEW_ORDER: 二重配列={nested} / {len(cur)}件 → {len(new_order)}件')
assert len(new_order) == len([e for e in events if e.get('genre') == 'new']), \
    'NEW_ORDERの件数が新着件数と合わない'

if not apply:
    print('\n(--apply で書き込み)')
    sys.exit(0)

dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
out = src[:m.start(2)] + dumped + src[m.end(2):]
# EVENTS を差し替えた後の文字列で NEW_ORDER を取り直して置換する
mo2 = re.search(r'(const NEW_ORDER\s*=\s*)(\[[\[\]0-9,\s]*\])(\s*;)', out)
flat = '[' + ', '.join(str(i) for i in new_order) + ']'
out = out[:mo2.start(2)] + flat + out[mo2.end(2):]
open(PATH, 'w', encoding='utf-8', newline='').write(out)
print('\n書き込み完了（NEW_ORDERは平らな配列に修復）')
