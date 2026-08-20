# -*- coding: utf-8 -*-
"""7/31の振り分けを戻す。ユーザーの「昨夜からの2件 振り分けOK」は
   3472 M-line Special / 3505 高嶋ちさ子 の2件だけの話だった。
   それ以外は genre:"new" に戻し、下書き(_genre/_extraGenres/_piaSub)も復元する。

戻し方は [[feedback_new_pool_ok_before_assign]] の「戻し方」に従う＝
   genre を "new" に／決めたジャンルは _genre に下書きで／NEW_ORDER も同じ件数に揃える。

id3475 キュウソネコカミの育成（枠1→6）は残す＝触るのは genre 系フィールドと NEW_ORDER だけ。

  python tmp/revert_assign_0731.py            # プラン
  python tmp/revert_assign_0731.py --apply
"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
KEEP_ASSIGNED = {3472, 3505}          # ユーザーがOKした2件はそのまま
BAK = 'index.html.bak_0731_assign'    # 振り分け直前の状態

hb = open(BAK, encoding='utf-8').read()
mb = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', hb, re.S)
OLD = {e['id']: e for e in json.loads(mb.group(2))}
mo_b = re.search(r'const\s+NEW_ORDER\s*=\s*(\[[^\]]*\])', hb)
OLD_ORDER = json.loads(mo_b.group(1))

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))

restored, kept = [], []
for e in EVENTS:
    o = OLD.get(e['id'])
    if not o or o.get('genre') != 'new':
        continue                      # 元から新着だった48件だけが対象
    if e['id'] in KEEP_ASSIGNED:
        kept.append('id=%d %s → %s のまま' % (e['id'], (e.get('name') or '')[:34], e.get('genre')))
        continue
    if e.get('genre') == 'new':
        continue                      # 3515（保留）はそのまま
    e['genre'] = 'new'
    for k in ('_genre', '_extraGenres', '_piaSub'):
        if k in o:
            e[k] = o[k]
        elif k in e:
            del e[k]
    if 'extraGenres' in o:
        e['extraGenres'] = o['extraGenres']
    elif 'extraGenres' in e:
        del e['extraGenres']
    restored.append('id=%d %s' % (e['id'], (e.get('name') or '')[:44]))

new_order = [i for i in OLD_ORDER if i not in KEEP_ASSIGNED]
pool = [e['id'] for e in EVENTS if e.get('genre') == 'new']

print('戻す: %d件 / OKの2件は据え置き: %d件' % (len(restored), len(kept)))
for s in kept:
    print('  ', s)
print('新着プール: %d件 / NEW_ORDER: %d件' % (len(pool), len(new_order)))
if sorted(pool) != sorted(new_order):
    print('!! プールとNEW_ORDERが不一致'); print(sorted(set(pool) ^ set(new_order))); sys.exit(1)

if not APPLY:
    print('(プランのみ。適用は --apply)'); sys.exit(0)

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
body = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
mo = re.search(r'(const\s+NEW_ORDER\s*=\s*)(\[[^\]]*\])', body)
body = body[:mo.start()] + mo.group(1) + json.dumps(new_order) + body[mo.end():]

bak = 'index.html.bak_%s_revert_assign' % datetime.date.today().strftime('%m%d')
open(bak, 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(body)
raw = open('index.html', 'rb').read()
print('=== 戻し適用 (backup: %s) / 孤立LF=%d ===' % (bak, raw.count(b'\n') - raw.count(b'\r\n')))
