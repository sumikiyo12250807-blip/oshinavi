# -*- coding: utf-8 -*-
"""heal_stale_deadlines の安全弁（2段め＝slot_key）を「売り場の番号」で比べるように直した確認（読むだけ・2026-09-14）。
  ①同じ売り場の2通りの書き方が同じ枠になる ②売り場の番号が違えば別の枠 ③番号の無いURLはそのまま比べる
  ④今日止まった6件を、書き込む前（96b56ad3）の登録と取り直し（tmp/heal_ids.json）で比べ直す
     ＝URLの書き方で止まった5件は2段めを通る／549 は1段め（売り切れの宮城9/19）で止まるまま
使い方: python tmp/test_heal_slotkey_0914.py
"""
import io
import json
import re
import subprocess
import sys

sys.path.insert(0, 'tools')
import heal_stale_deadlines as H

sys.stdout.reconfigure(encoding='utf-8')
a = {'type': 'プレリザーブ（北海道 R9年 5/15公演）9/14 11:00発売', 'url': 'https://ticket.pia.jp/pia/event.do?eventCd=2633839'}
b = {'type': 'プレリザーブ（北海道 R9年 5/15公演）〜9/27 23:59', 'url': 'https://t.pia.jp/pia/event/event.do?eventCd=2633839'}
c = {'type': 'プレリザーブ（北海道 R9年 5/15公演）〜9/27 23:59', 'url': 'https://t.pia.jp/pia/event/event.do?eventCd=2633840'}
d = {'type': '一般発売（東京 9/1公演）', 'url': 'https://eplus.jp/sf/detail/1234'}
assert H.slot_key(a) == H.slot_key(b), (H.slot_key(a), H.slot_key(b))
assert H.slot_key(b) != H.slot_key(c)
assert H.slot_key(d)[1] == 'https://eplus.jp/sf/detail/1234'
print('①②③ OK')

TODAY = '2026-09-14'
old_src = subprocess.run(['git', 'show', '96b56ad3:index.html'], capture_output=True).stdout.decode('utf-8')
old = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', old_src, re.S).group(1))}
built = {o['id']: o for o in json.load(io.open('tmp/heal_ids.json', encoding='utf-8'))}
for i in [549, 5155, 5332, 5411, 7326, 8405]:
    e, o = old[i], built[i]
    live_old = {H.perf_key(t.get('type')) for t in e['tickets'] if (t.get('date') or '') >= TODAY}
    live_new = {H.perf_key(t.get('type')) for t in o['tickets'] if (t.get('date') or '') >= TODAY}
    vis_old = {H.slot_key(t) for t in e['tickets'] if H.visible_slot(t, TODAY)
               and (not (t.get('url') or '') or 'pia.jp' in (t.get('url') or ''))}
    vis_new = {H.slot_key(t) for t in o['tickets'] if H.visible_slot(t, TODAY)}
    print('id%-5s 1段め(公演)で消える %s ／ 2段め(券種＋売り場)で消える %s' % (
        i, sorted(live_old - live_new) or 'なし', sorted(k[0] for k in vis_old - vis_new) or 'なし'))
