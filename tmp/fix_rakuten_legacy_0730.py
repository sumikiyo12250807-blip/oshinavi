# -*- coding: utf-8 -*-
"""楽天ビルダーの締切バグ(win_end_iso)が既存エントリに残した誤りを、実ページの一次情報で直す。

① id=1768 Na Pookela ナーポオケラ 2026
   「一般発売 8/15 10:00発売」が date==startDate の**単日形(隠れ枠)**になっていた。
   実ページの公演カード sale_end は 2026-09-16 23:59。ヒールはぴあ専用なので、
   このままだと 8/15 を過ぎた瞬間に画面から消えて誰も直せない（[[feedback_delete_nonpia_blindspot]]）。

② id=3220 バイきんぐ単独ライブ「暴音」
   5県を名乗る枠が1つだけで、締切は東京の 8/27 のみ。実際は会場ごとに締切が違う
   （大阪8/1公演→7/31 / 石川8/8→8/7 / 宮城8/22→8/21 / 東京8/28→8/27）。
   このままだと大阪の客に「8/27まで買える」と嘘をつく。販売日ごとに枠を分ける
   （[[feedback_tour_badge_split_by_saledate]]）。愛知7/31公演はページから消滅＝買えないので載せない。

CRLF保護＝inject_built.py と同じ流儀（newline='' で読み、改行を明示的に揃えて書く）。
"""
import json
import re

h = open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

log = []

# ---- ① 1768 ----
e = byid[1768]
hit = 0
for t in e['tickets']:
    if t.get('startDate') == '2026-08-15' and t.get('date') == '2026-08-15':
        t['date'] = '2026-09-16'
        t['type'] = '一般発売（神奈川 9/20〜9/21公演）8/15 10:00発売 〜9/16 23:59'
        hit += 1
assert hit == 1, f'1768 の対象枠が {hit} 件（1件のはず）'
log.append('id=1768 Na Pookela ナーポオケラ 2026')
log.append('   一般発売 date 2026-08-15(単日形) → 2026-09-16 / バッジに「〜9/16 23:59」を追加')

# ---- ② 3220 ----
e = byid[3220]
url = e['tickets'][0].get('url') or (e.get('links') or {}).get('rakuten')
before = [t.get('type') for t in e['tickets']]
assert len(e['tickets']) == 1, f'3220 の枠が {len(e["tickets"])} 件（1件のはず）'
NEW = [
    ('大阪', '8/1', '2026-07-31', '7/31'),
    ('石川', '8/8', '2026-08-07', '8/7'),
    ('宮城', '8/22', '2026-08-21', '8/21'),
    ('東京', '8/28', '2026-08-27', '8/27'),
]
tickets = []
for pref, perf, iso, mdd in NEW:
    t = {'type': f'一般発売（{pref} {perf}公演）〜{mdd} 23:59', 'date': iso}
    if url:
        t['url'] = url
    tickets.append(t)
e['tickets'] = tickets
log.append('')
log.append('id=3220 バイきんぐ単独ライブ「暴音」')
log.append(f'   旧: {before[0]}')
log.append('   新: 会場ごとに4枠へ分割（愛知7/31公演はページから消滅＝買えないので載せない）')
for t in tickets:
    log.append(f'       {t["type"]}  [date={t["date"]}]')

open('index.html.bak_0730_rakfix', 'w', encoding='utf-8', newline='').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])

log.append('')
log.append('=== 2件修正 (backup: index.html.bak_0730_rakfix) ===')
open('tmp/fix_rakuten_legacy_0730.txt', 'w', encoding='utf-8').write('\n'.join(log))
print('wrote tmp/fix_rakuten_legacy_0730.txt')
