"""新着50件(id3420-3469)の振り分け。
方針＝[[project_vendor_genre_autoassign]]「_genre をそのまま genre に移す・自分で再分類しない」。
extraGenres は公演名に対象層が明記されている4件だけ追加（[[feedback_genre_both_when_unclear]]）。
CRLF保護＝読みは universal newlines、書きは text モード（newline='' は使わない・7/29の事故）。
"""
import json
import re

# 追加する extraGenres（下書きが空の子だけ・主ジャンルは動かさない）
EXTRA = {
    3426: ['kids'],    # 狂言ござる乃座「～親子編～」＝親子向けと公演名に明記
    3436: ['kids'],    # さかなクンのおさかな教室＝子ども向け教室
    3464: ['anime'],   # 昭和ライダー列伝＝特撮トーク（アニメ枠のファン層）
    3465: ['anime'],   # スキップとローファー展＝漫画原作の展覧会
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
if not m:
    raise SystemExit('EVENTS が見つからない')
EVENTS = json.loads(m.group(2))

log = []
n = 0
tally = {}
for e in EVENTS:
    if e.get('genre') != 'new':
        continue
    g = e.get('_genre')
    if not g:
        raise SystemExit(f"id={e['id']} の _genre が空＝止める（人の判断が要る）")
    extra = list(e.get('_extraGenres') or [])
    for x in EXTRA.get(e['id'], []):
        if x not in extra:
            extra.append(x)
    e['genre'] = g
    if extra:
        e['extraGenres'] = extra
    elif 'extraGenres' in e:
        del e['extraGenres']
    piasub = e.get('_piaSub')
    for k in ('_genre', '_extraGenres', '_piaSub'):
        if k in e:
            del e[k]
    tally[g] = tally.get(g, 0) + 1
    n += 1
    log.append(f"id={e['id']:<5} → {g}{'+' + ','.join(extra) if extra else ''}   ({piasub})  {(e.get('artist') or '')[:40]}")

left = sum(1 for e in EVENTS if e.get('genre') == 'new')
if left:
    raise SystemExit(f'genre:new が {left} 件残っている＝止める')

# 残留下書きフィールドが無いか全件確認
resid = [e['id'] for e in EVENTS if any(k in e for k in ('_genre', '_extraGenres', '_piaSub'))]
if resid:
    raise SystemExit(f'下書きフィールドが残っている: {resid[:10]}')

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
body = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]

# NEW_ORDER を空に（配列だけ残ると空タブになる）
mo = re.search(r'(const\s+NEW_ORDER\s*=\s*)(\[[^\]]*\])', body)
if not mo:
    raise SystemExit('NEW_ORDER が見つからない')
before_order = mo.group(2)
body = body[:mo.start()] + mo.group(1) + '[]' + body[mo.end():]

open('index.html.bak_0730_assign', 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(body)

log.append('')
log.append(f'=== 振り分け {n} 件 / genre:new 残 0 / NEW_ORDER {len(json.loads(before_order))}件 → 0件 ===')
log.append('集計: ' + ' / '.join(f'{k}{v}' for k, v in sorted(tally.items(), key=lambda x: -x[1])))
open('tmp/assign_0730.txt', 'w', encoding='utf-8').write('\n'.join(log))
print(f'wrote tmp/assign_0730.txt  assigned={n}  backup=index.html.bak_0730_assign')
