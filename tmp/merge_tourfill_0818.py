# -*- coding: utf-8 -*-
"""ツアーの取りこぼし公演を既存エントリに統合する（2026-08-18 ユーザー指摘）。

ぴあの「まとめページ」には出ないのに、アーティスト名で検索すると出てくる公演がある。
（ハンブレッダーズ名古屋10/30・杉山清貴の八王子/四国・来生たかおの長野/北海道/秋田）
build_pia_entries に全URLを渡して作り直した結果から、**tickets / 会場 / 都道府県 / 公演日**
だけを既存エントリへ移す。id・genre・name・links.pia・amazon は触らない。

[[feedback_tour_consolidate]] ツアーは1エントリ
[[feedback_tour_per_ticket_url]] 各枠に会場別URLを付ける
[[feedback_capture_all_not_select]] 買える枠は1つ残らず載せる
"""
import io, json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
BUILT = json.load(io.open('tmp/tourfill_built_0818.json', encoding='utf-8-sig'))
by_new = {e['id']: e for e in BUILT}

h = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

MOVE = ('tickets', 'venue', 'prefecture', 'date', 'dateLabel')

for ev in EVENTS:
    nb = by_new.get(ev['id'])
    if not nb:
        continue
    print('=== id%s %s' % (ev['id'], ev.get('artist')))
    for k in MOVE:
        old, new = ev.get(k), nb.get(k)
        if k == 'tickets':
            print('   枠 %d → %d' % (len(old or []), len(new or [])))
        elif old != new:
            print('   %s: %s → %s' % (k, old, new))
        if new is not None:
            ev[k] = new

if not APPLY:
    print('\n（判定のみ。適用は --apply）')
    sys.exit(0)

bak = 'index.html.bak_0818_tourfill'
if not os.path.exists(bak):
    io.open(bak, 'w', encoding='utf-8').write(h)

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
io.open('index.html', 'w', encoding='utf-8').write(h2)
print('\n=== 適用完了 (backup: %s) ===' % bak)
