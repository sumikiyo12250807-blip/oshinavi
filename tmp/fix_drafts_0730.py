# -*- coding: utf-8 -*-
"""投入済み新着の _genre 下書きを補正する（genre は "new" のまま＝振り分けはユーザー合図後）。

根拠は既存エントリの前例（[[feedback_check_existing_logic]]）とぴあの _piaSub：
  3513 大相撲九月場所      engeki → sports  ＝既存の大相撲8件が全部 sports
  3511 アクアパーク品川    engeki → kids    ＝既存「名古屋港水族館 入館券」(2388)が kids ／_piaSub=アミューズメント
  3507 おかあさんといっしょ engeki → kids    ＝既存(2552)が kids ／_piaSub=子供と楽しむ
  3512 わんにゃん夜ふかし縁日 engeki → kids  ＝_piaSub=スクール・レジャー
残す（⚠️相談）＝3510 竜王戦前夜祭（_piaSub=イベントその他・前例なし）／3505 高嶋ちさ子（_piaSub空）。
"""
import json
import re

FIX = {3513: 'sports', 3511: 'kids', 3507: 'kids', 3512: 'kids'}

h = open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

log = []
for e in EVENTS:
    g = FIX.get(e.get('id'))
    if not g:
        continue
    assert e.get('genre') == 'new', f"id={e['id']} は genre:new でない（振り分け済みを触ってはいけない）"
    old = e.get('_genre')
    e['_genre'] = g
    log.append(f"id={e['id']} {(e.get('artist') or '')[:44]}  _genre {old} → {g}")

assert len(log) == len(FIX), f'対象 {len(log)}/{len(FIX)} 件しか当たっていない'

open('index.html.bak_0730_drafts', 'w', encoding='utf-8', newline='').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
log.append('')
log.append(f'=== 下書き {len(log) - 1}件 補正 (backup: index.html.bak_0730_drafts) ===')
open('tmp/fix_drafts_0730.txt', 'w', encoding='utf-8').write('\n'.join(log))
print('wrote tmp/fix_drafts_0730.txt')
