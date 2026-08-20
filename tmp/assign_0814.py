# -*- coding: utf-8 -*-
"""新着プール45件をジャンル振り分けする（ユーザー明示「新着45件振り分けおねがいね」2026-08-14）。

原則＝harvest時にぴあカテゴリから記憶した `_genre`/`_extraGenres` をそのまま `genre` へ移す。
自分の音楽知識で再分類しない（[[project_vendor_genre_autoassign]]）。

例外＝⚠️相談4件だけ。ぴあが「イベント/…」という**形式のカテゴリ**を付けていて音楽ジャンルを
返していない子は、2026-08-01のユーザー明示「ジャンルは主役（アーティスト）で決まる」に従って読み直す。

  4190 ファミリークリスマスコンサート  classic → classic + kids（ぴあ=クラシックその他・ファミリー向け）
  4211 ウィーン・フィル奏者マスタークラス classic のまま（ぴあ=クラシックその他）
  4224 LEE JI HOON FANMEETING     engeki → kpop（ぴあ=ショー・ファンイベント／主役は韓国俳優イ・ジフン）
  4225 松浦航大 歌まねライブ            engeki → jpop + owarai（ぴあ=学園祭／主役は歌手・ものまねタレント）
"""
import re, json, io, sys, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
APPLY = '--apply' in sys.argv
PATH = 'index.html'

OVERRIDE = {
    4190: ('classic', ['kids']),
    4211: ('classic', []),
    4224: ('kpop', []),
    4225: ('jpop', ['owarai']),
}

h = open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))
pool = [e for e in EV if e.get('genre') == 'new']
print('新着プール %d件' % len(pool))

count = {}
for e in sorted(pool, key=lambda x: x['id']):
    i = e['id']
    if i in OVERRIDE:
        g, extra = OVERRIDE[i]
        mark = '⚠️'
    else:
        g, extra = e.get('_genre'), list(e.get('_extraGenres') or [])
        mark = '  '
    if not g:
        print('🚨 id=%d は _genre が空＝止める' % i)
        sys.exit(1)
    print('%s %d %-9s %-10s %s' % (mark, i, g, '+' + ','.join(extra) if extra else '', (e.get('name') or '')[:34]))
    count[g] = count.get(g, 0) + 1
    e['genre'] = g
    if extra:
        e['extraGenres'] = extra
    else:
        e.pop('extraGenres', None)
    for k in ('_genre', '_extraGenres', '_piaSub'):
        e.pop(k, None)

print('\n内訳: ' + ' / '.join('%s%d' % (k, v) for k, v in sorted(count.items(), key=lambda x: -x[1])))

if not APPLY:
    print('\n（提案のみ。適用は --apply）')
    sys.exit(0)

bak = PATH + '.bak_0814_assign'
open(bak, 'w', encoding='utf-8', newline='').write(h)
body = json.dumps(EV, ensure_ascii=False, indent=2)
if '\r\n' in h:
    body = body.replace('\r\n', '\n').replace('\n', '\r\n')
out = h[:m.start(2)] + body + h[m.end(2):]

# NEW_ORDER は新着プールの並び順配列。振り分けたら空にする（残すと空のタブが並ぶ）。
mo = re.search(r'(NEW_ORDER\s*=\s*)(\[[^\]]*\])', out)
if mo:
    print('NEW_ORDER %d件 → 0件' % len(json.loads(mo.group(2))))
    out = out[:mo.start(2)] + '[]' + out[mo.end(2):]

open(PATH, 'w', encoding='utf-8', newline='').write(out)
print('\n=== 振り分け適用 (backup: %s) ===' % bak)
