# -*- coding: utf-8 -*-
"""3472 / 3505 を新着プールに戻して48件そろえる（ユーザーがまだチェックしていなかったため）。
決まったジャンルは下書き(_genre/_extraGenres)として持たせ、チェック完了後の振り分けで使う。
NEW_ORDER は振り分け直前のバックアップの並び（id昇順48件）をそのまま復元＝チェック位置を動かさない。

  python tmp/restore48_0731.py            # プラン
  python tmp/restore48_0731.py --apply
"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
BACK = {3472: ('idol', ['jpop']), 3505: ('classic', [])}
BAK = 'index.html.bak_0731_assign'

hb = open(BAK, encoding='utf-8').read()
OLD_ORDER = json.loads(re.search(r'const\s+NEW_ORDER\s*=\s*(\[[^\]]*\])', hb).group(1))

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))

done = []
for e in EVENTS:
    if e['id'] not in BACK:
        continue
    g, extra = BACK[e['id']]
    e['genre'] = 'new'
    e['_genre'] = g
    if extra:
        e['_extraGenres'] = extra
    elif '_extraGenres' in e:
        del e['_extraGenres']
    if 'extraGenres' in e:
        del e['extraGenres']
    done.append('id=%d %s → 新着へ戻す（下書き %s%s）'
                % (e['id'], (e.get('name') or '')[:40], g, '+' + ','.join(extra) if extra else ''))

pool = [e['id'] for e in EVENTS if e.get('genre') == 'new']
for s in done:
    print(' -', s)
print('新着プール: %d件 / NEW_ORDER復元: %d件' % (len(pool), len(OLD_ORDER)))
if sorted(pool) != sorted(OLD_ORDER):
    print('!! 不一致:', sorted(set(pool) ^ set(OLD_ORDER))); sys.exit(1)
if len(done) != 2:
    print('!! 対象が2件でない'); sys.exit(1)

if not APPLY:
    print('(プランのみ。適用は --apply)'); sys.exit(0)

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
body = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
mo = re.search(r'(const\s+NEW_ORDER\s*=\s*)(\[[^\]]*\])', body)
body = body[:mo.start()] + mo.group(1) + json.dumps(OLD_ORDER) + body[mo.end():]

bak = 'index.html.bak_%s_restore48' % datetime.date.today().strftime('%m%d')
open(bak, 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(body)
raw = open('index.html', 'rb').read()
print('=== 適用 (backup: %s) / 孤立LF=%d ===' % (bak, raw.count(b'\n') - raw.count(b'\r\n')))
