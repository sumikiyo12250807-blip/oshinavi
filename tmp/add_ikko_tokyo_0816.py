# -*- coding: utf-8 -*-
"""IKKO DRAMATIC(id4226) に e+ の東京9/29公演（昼夜2回）を追加する。
根拠＝https://eplus.jp/sf/detail/4549290001-P0030001P021001 (14:00) / -P021002 (18:00)
  タイトル「IKKO DRAMATIC ～BEAUTY MUSIC SHOW～のチケット情報(2026/9/29(火))」会場 ニッショーホール
  先着 一般発売 受付 2026/6/26 10:00〜2026/9/23(水・祝)18:00・受付中
ぴあには無くe+だけで売っている枠（harvestはぴあ専業なので落ちていた）。
同日同会場で時間違いなのでバッジに公演時刻を入れる（feedback_same_day_show_time_badge）。
"""
import re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

NEW = [
    {"type": "一般発売（東京 9/29 14:00公演）〜9/23 18:00", "date": "2026-09-23",
     "url": "https://eplus.jp/sf/detail/4549290001-P0030001P021001"},
    {"type": "一般発売（東京 9/29 18:00公演）〜9/23 18:00", "date": "2026-09-23",
     "url": "https://eplus.jp/sf/detail/4549290001-P0030001P021002"},
]

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

for e in EVENTS:
    if e.get('id') != 4226:
        continue
    tks = e.setdefault('tickets', [])
    have = {t.get('url') for t in tks}
    add = [t for t in NEW if t['url'] not in have]
    if not add:
        print("既に登録済み"); sys.exit(0)
    tks[:0] = add                      # 9/23締切は既存(8/22・9/12)より後ろだが、並びはdate昇順に整える
    tks.sort(key=lambda t: (t.get('date') or ''))
    e['dateLabel'] = "2026年9月29日(火) 東京 ニッショーホール ／ 11月8日(日) 大阪 新歌舞伎座"
    e['venue'] = "ニッショーホール／新歌舞伎座"
    e['prefecture'] = "東京・大阪"
    e['links']['eplus'] = "https://eplus.jp/sf/detail/4549290001-P0030001P021001"
    for t in add:
        print("枠追加:", t['type'])
    print("dateLabel :", e['dateLabel'])
    break
else:
    print("id4226 が見つからない"); sys.exit(1)

bak = 'index.html.bak_0816_ikko'
if not os.path.exists(bak):
    open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("=== 適用 (backup: %s) ===" % bak)
