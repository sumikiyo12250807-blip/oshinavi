# -*- coding: utf-8 -*-
"""ゴルトベルク変奏曲2027 を id2841 に統合し 2842 を削除する。
   🚨 2841は既に振り分け済み(classic)なので genre は classic のまま維持し、
      ビルダーが返す genre:"new" や下書き(_genre等)は持ち込まない（新着タブに逆戻りさせない）。
   使い方: python tmp/goldberg_apply_0727.py [--apply]
"""
import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = 'index.html'
apply = '--apply' in sys.argv
KEEP, DROP = 2841, [2842]

built = json.load(open('tmp/goldberg.json', encoding='utf-8'))['built']
src = open(PATH, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by_id = {e['id']: e for e in events}

merged_urls = {t['url'] for t in built['tickets']}
for eid in [KEEP] + DROP:
    e = by_id[eid]
    own = (e.get('links') or {}).get('pia')
    assert own in merged_urls, f'id{eid} のURL {own} が統合後の枠に無い'
    print(f'  id{eid} {e["name"][:40]} / {e["prefecture"]} → 枠が統合先に存在 OK')
assert len(built['tickets']) == 2, '枠数が2でない'

k = by_id[KEEP]
before_genre = k.get('genre')
for f in ('artist', 'name', 'date', 'dateLabel', 'venue', 'prefecture',
          'tickets', 'links', 'verifiedAt'):
    k[f] = built[f]
k['genre'] = before_genre                    # classic を維持（newに戻さない）
for f in ('_genre', '_extraGenres', '_piaSub', '_srcgenre'):
    k.pop(f, None)                           # 下書きは持ち込まない
assert k['genre'] == 'classic', k['genre']

print(f'\n=== 統合後 id{KEEP} ===')
print(' name :', k['name'], '| genre:', k['genre'])
print(' venue:', k['venue'])
print(' label:', k['dateLabel'])
for t in k['tickets']:
    print('  枠:', t['type'], '|', t['url'])

events = [e for e in events if e['id'] not in DROP]
print(f'\n削除: {DROP}（欠番のまま残す）')

if not apply:
    print('\n(--apply で書き込み)')
    sys.exit(0)

dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
open(PATH, 'w', encoding='utf-8', newline='').write(src[:m.start(2)] + dumped + src[m.end(2):])
print('\n書き込み完了')
