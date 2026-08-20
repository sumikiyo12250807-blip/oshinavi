# -*- coding: utf-8 -*-
"""『クリスマス』4件を id3298 に統合し、3299/3300/3301 を消して NEW_ORDER も詰める。
   memory: feedback_tour_consolidate / feedback_tour_per_ticket_url /
           feedback_new_list_order_lock（id据え置き・削除は欠番）/ feedback_index_html_crlf_preserve
   使い方: python tmp/igarashi_apply_0727.py [--apply]
"""
import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = 'index.html'
apply = '--apply' in sys.argv
KEEP, DROP = 3298, [3299, 3300, 3301]
NAME = '五十嵐紅|ギターと静寂『クリスマス』'

built = json.load(open('tmp/igarashi_merge.json', encoding='utf-8'))['built']
src = open(PATH, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by_id = {e['id']: e for e in events}

# 安全確認: 消す3件の枠が、統合後に全部残っているか（買える枠を落とさない）
merged_urls = {t['url'] for t in built['tickets']}
for eid in [KEEP] + DROP:
    e = by_id[eid]
    assert e.get('genre') == 'new', f'id{eid} が新着でない'
    own = (e.get('links') or {}).get('pia')
    assert own in merged_urls, f'id{eid} のURL {own} が統合後の枠に無い'
    print(f'  id{eid} {e["name"][:44]} → 枠が統合先に存在 OK')
assert len(built['tickets']) == 4, '枠数が4でない'

k = by_id[KEEP]
k['artist'] = NAME
k['name'] = NAME
for f in ('date', 'dateLabel', 'venue', 'prefecture', 'tickets', 'links', 'verifiedAt'):
    k[f] = built[f]
k['links']['amazon'] = (by_id[3300].get('links') or {}).get('amazon')  # 『クリスマス』のCD検索を維持

print(f'\n=== 統合後 id{KEEP} ===')
print(' name :', k['name'])
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
out = src[:m.start(2)] + dumped + src[m.end(2):]
# NEW_ORDER から消したidを外す
mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', out)
cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
new_order = [i for i in cur if i not in DROP]
out = out[:mo.start(2)] + '[' + ', '.join(str(i) for i in new_order) + ']' + out[mo.end(2):]
open(PATH, 'w', encoding='utf-8', newline='').write(out)
print(f'\n書き込み完了 / NEW_ORDER {len(cur)}→{len(new_order)}件')
