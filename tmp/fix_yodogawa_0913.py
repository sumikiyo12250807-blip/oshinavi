# -*- coding: utf-8 -*-
"""なにわ淀川花火大会を1エントリに畳む（2026-09-13・ユーザー「淀川畳んで」）。

いまの形＝id2535 は「ぴあシート／ぴあプラチナペアシート」だけのエントリ。
本体（納涼船席）は 9/12 の新着で拾ったが、どちらに寄せるか決まらず保留にしていた（tmp/hold_new_0912.json の id8322）。

やること
  ① 既存の枠（ぴあシート）に飛び先 eventCd=2624362 を焼き込む
     🚨畳む前にURLを焼く＝枠数だけ見ても飛び先の破壊は見えない（memory feedback_tour_per_ticket_url）
  ② その枠は生HTMLで「予定枚数終了」＝消さずに印を付ける（memory feedback_soldout_keep_visible）
  ③ 納涼船席の2枠（eventCd=2635910・生HTMLで「販売期間中」）を足す
  ④ 名前から「ぴあシート／ぴあプラチナペアシート」を外す＝もう限定エントリではない

使い方: python tmp/fix_yodogawa_0913.py [--apply]
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
TODAY = '2026-09-13'
U_SHEET = 'https://t.pia.jp/pia/event/event.do?eventCd=2624362'
U_BOAT = 'https://t.pia.jp/pia/event/event.do?eventCd=2635910'

path = 'index.html'
src = io.open(path, encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
ev = json.loads(m.group(2))
e = next((x for x in ev if x['id'] == 2535), None)
assert e, 'id2535 が無い'

ts = e['tickets']
assert len(ts) == 1, '既存の枠が1本でない＝手順を見直す（いま%d本）' % len(ts)

# ①② 既存のぴあシート枠
t = ts[0]
t['type'] = '一般発売【ぴあシート／ぴあプラチナペアシート】（大阪 10/17公演）〜10/16 23:59'
t['url'] = U_SHEET
t['soldout'] = True
t['soldoutSince'] = TODAY
print('①② ぴあシートの枠に飛び先を焼いて、予定枚数終了の印を付けた')

# ③ 納涼船席（ぴあの生HTMLで「販売期間中」）
for name in ('専用ハイヤー送迎付き', '送迎無し'):
    ts.append({
        'type': '一般発売【納涼船席/%s】（大阪 10/17公演）〜10/11 23:59' % name,
        'date': '2026-10-11',
        'url': U_BOAT,
    })
print('③ 納涼船席の枠を2本足した')

# ④ 名前
e['name'] = '第38回なにわ淀川花火大会'
e['artist'] = '第38回なにわ淀川花火大会'
print('④ 名前を「第38回なにわ淀川花火大会」に')

print('枠 1本 → %d本' % len(ts))
if not APPLY:
    print('（--apply で適用）')
    sys.exit(0)
io.open('index.html.bak_0913_yodogawa', 'w', encoding='utf-8').write(src)
io.open(path, 'w', encoding='utf-8').write(
    src[:m.start()] + m.group(1) + json.dumps(ev, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
print('✅ 適用したわ（backup: index.html.bak_0913_yodogawa）')
