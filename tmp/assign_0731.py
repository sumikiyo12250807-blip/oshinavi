# -*- coding: utf-8 -*-
"""新着48件の振り分け（2026-07-31・ユーザー「振り分けOK」後）。
方針＝[[project_vendor_genre_autoassign]]「_genre をそのまま genre に移す・自分で再分類しない」。

人が決めた2件（_piaSub が空でぴあカテゴリから決められなかった分・ユーザー7/31 OK）:
  3472 M-line Special 2026 Autumn ～NOCTURNE～ → idol（+jpop）※実態はライブハウスの音楽ライブ
  3505 高嶋ちさ子のザワつく!音楽会 2026      → classic

保留2件（振り分けない・新着に残す＝ユーザー未回答）:
  3510 第39期竜王戦第2局三島対局 前夜祭＝ぴあ「イベント/イベントその他」で名前fallbackが engeki に倒れた。
       将棋なので sports 提案中・返事待ち。
  3515 ウルトラヒーローズ THE LIVE（楽天版）＝既存 id2544（ぴあ版）と同じツアーの二重登録。
       統合方針をユーザーが決めるまで genre:"new" のまま置く。

CRLF保護＝読みは universal newlines、書きは text モード（newline='' は使わない）。
  python tmp/assign_0731.py          # プランだけ出す
  python tmp/assign_0731.py --apply  # 適用
"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
HOLD = {3510, 3515}
FORCE = {3472: ('idol', ['jpop']), 3505: ('classic', [])}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
if not m:
    raise SystemExit('EVENTS が見つからない')
EVENTS = json.loads(m.group(2))

log, tally, n = [], {}, 0
for e in EVENTS:
    if e.get('genre') != 'new':
        continue
    if e['id'] in HOLD:
        log.append('id=%-5d 保留（新着のまま） %s' % (e['id'], (e.get('name') or '')[:44]))
        continue
    if e['id'] in FORCE:
        g, extra = FORCE[e['id']][0], list(FORCE[e['id']][1])
    else:
        g = e.get('_genre')
        if not g:
            raise SystemExit('id=%d の _genre が空＝止める（人の判断が要る）' % e['id'])
        extra = list(e.get('_extraGenres') or [])
    piasub = e.get('_piaSub')
    if APPLY:
        e['genre'] = g
        if extra:
            e['extraGenres'] = extra
        elif 'extraGenres' in e:
            del e['extraGenres']
        for k in ('_genre', '_extraGenres', '_piaSub'):
            if k in e:
                del e[k]
    tally[g] = tally.get(g, 0) + 1
    n += 1
    log.append('id=%-5d → %s%s   (%s)  %s' % (
        e['id'], g, '+' + ','.join(extra) if extra else '', piasub or '-', (e.get('name') or '')[:44]))

log.append('')
log.append('=== 振り分け %d 件 / 保留 %d 件 ===' % (n, len(HOLD)))
log.append('集計: ' + ' / '.join('%s%d' % (k, v) for k, v in sorted(tally.items(), key=lambda x: -x[1])))
txt = '\n'.join(log)
open('tmp/assign_0731.txt', 'w', encoding='utf-8').write(txt)
print(txt)

if not APPLY:
    print('\n(プランのみ。適用は --apply)')
    raise SystemExit(0)

left = [e['id'] for e in EVENTS if e.get('genre') == 'new']
if sorted(left) != sorted(HOLD):
    raise SystemExit('genre:new の残りが想定外: %s' % left)
resid = [e['id'] for e in EVENTS if e['id'] not in HOLD and any(k in e for k in ('_genre', '_extraGenres', '_piaSub'))]
if resid:
    raise SystemExit('下書きフィールドが残っている: %s' % resid[:10])

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
body = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]

mo = re.search(r'(const\s+NEW_ORDER\s*=\s*)(\[[^\]]*\])', body)
if not mo:
    raise SystemExit('NEW_ORDER が見つからない')
before_order = len(json.loads(mo.group(2)))
body = body[:mo.start()] + mo.group(1) + json.dumps(sorted(HOLD)) + body[mo.end():]

open('index.html.bak_0731_assign', 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(body)
print('\n=== 適用 / NEW_ORDER %d件 → %d件 / backup=index.html.bak_0731_assign ===' % (before_order, len(HOLD)))
