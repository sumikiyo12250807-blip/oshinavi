# -*- coding: utf-8 -*-
"""id5411「他人」に岡山公演を足し、先行の会場表記をぴあの今の形に揃える（2026-09-13 朝）。

見つけ方＝朝の発売前スイープの全行と登録を突き合わせる window_gap_0913.py
（memory feedback_existing_entries_miss_new_windows＝登録済みページにぴあが後から足した窓）。
ぴあ bundle b2671016 を機械で作り直したら、会場が4つ（東京・大阪・岡山・福岡）に増えていて、
登録は福岡・大阪の2つしか持っていなかった。

やること
  ① 岡山の一般発売（9/19 10:00発売）を足す
  ② 先行の券種名「（大阪 R9年 1/22〜1/24公演）」→「（東京・大阪 R9年 1/15〜1/24公演）」に揃える
     ＝丸ごと足すと同じ売り場が2枠に割れる（二重登録）ので、既存の枠を書き換える
  ③ venue／prefecture／dateLabel を4会場ぶんに広げる
🚨 dateLabel は「これから行われる公演」の事実の会期（memory feedback_show_true_dates_not_sellable_range）。
   2026/11/22 福岡 〜 2027/1/24 大阪。今日(9/13)より前の公演は無い。
🚨 各枠の飛び先URLは残す（memory feedback_tour_per_ticket_url）。岡山と先行はどちらも bundle が売り場。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
BUNDLE = 'https://ticket.pia.jp/pia/event.do?eventBundleCd=b2671016'
path = 'index.html'
src = io.open(path, encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
ev = json.loads(m.group(2))

done = []
for e in ev:
    if e['id'] != 5411:
        continue
    ts = e['tickets']
    if any('岡山' in (t.get('type') or '') for t in ts):
        print('岡山の枠はもうある＝中止')
        sys.exit(1)
    for t in ts:
        if (t.get('type') or '').startswith('プレイガイド最速先行'):
            t['type'] = 'プレイガイド最速先行（東京・大阪 R9年 1/15〜1/24公演）9/14 10:00発売'
            done.append('先行の券種名を揃えた')
    ts.insert(0, {
        'type': '一般発売（岡山 12/19〜12/20公演）9/19 10:00発売',
        'date': '2026-09-19',
        'startDate': '2026-09-19',
        'url': BUNDLE,
    })
    done.append('岡山の一般発売を足した')
    e['venue'] = '全国ツアー（J:COM北九州芸術劇場 小劇場／岡山芸術創造劇場 ハレノワ 小劇場／本多劇場／ABCホール）'
    e['prefecture'] = '福岡・岡山・東京・大阪'
    e['dateLabel'] = '2026年11月22日(日)〜2027年1月24日(日) 福岡・岡山・東京・大阪'
    done.append('会場と日付の欄を4会場ぶんに広げた')

print('\n'.join(done) or '対象なし')
if not APPLY:
    print('（--apply で適用）')
    sys.exit(0)
io.open('index.html.bak_0913_fix5411', 'w', encoding='utf-8').write(src)
out = src[:m.start()] + m.group(1) + json.dumps(ev, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():]
io.open(path, 'w', encoding='utf-8').write(out)
print('✅ 適用したわ（backup: index.html.bak_0913_fix5411）')
