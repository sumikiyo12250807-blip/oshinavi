# -*- coding: utf-8 -*-
"""18時のあとのヒール（--ids・tmp/heal_ids.json）で安全弁が止めた35件を仕分ける（2026-09-14 夜）。
静かなぴあで取り直しても35件止まった＝混雑ページではない。止まった枠を見ると、売り切れの印を付けて出し続けている枠
（2500 ドラクエ 千葉9/23 など）＝ぴあで買えないので取り直しに入らず、安全弁が「消える」と数える（昼の 549 坂本冬美と同じ型）。
仕分け:
  ・消えると数えた枠が**全部売り切れの印付き**のエントリ → 取り直した枠に差し替え＋売り切れの枠（今日以降）とぴあ以外の枠は残す
    （取り直しに発売日が無い枠は、元の同じ公演の枠の startDate を引き継ぐ）
  ・印の付いていない枠が消えるエントリ → 触らずに一覧に出す（ぴあの実物で1件ずつ確かめる）
使い方: python tmp/heal_blocked_keep_soldout_1805.py [--apply]
"""
import datetime
import io
import json
import re
import sys

sys.path.insert(0, 'tools')
import heal_stale_deadlines as H

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
built = {o['id']: o for o in json.load(io.open('tmp/heal_ids.json', encoding='utf-8')) if o.get('status') == 'convert'}

apply_ids, hold = [], []
for i, o in sorted(built.items()):
    e = by.get(i)
    if not e:
        continue
    old = e.get('tickets') or []
    new = [dict(t) for t in o['tickets']]
    live_old = {H.perf_key(t.get('type')) for t in old if (t.get('date') or '') >= TODAY}
    live_new = {H.perf_key(t.get('type')) for t in new if (t.get('date') or '') >= TODAY}
    lost_perf = live_old - live_new
    vis_old = {H.slot_key(t) for t in old if H.visible_slot(t, TODAY) and (not (t.get('url') or '') or 'pia.jp' in (t.get('url') or ''))}
    vis_new = {H.slot_key(t) for t in new if H.visible_slot(t, TODAY)}
    lost_slot = vis_old - vis_new
    if not lost_perf and not lost_slot:
        continue  # 安全弁を通った＝もう当たっている
    # 消えると数えた枠の元の枠が、全部売り切れの印付きか
    lost_tix = [t for t in old if (t.get('date') or '') >= TODAY and
                (H.perf_key(t.get('type')) in lost_perf or H.slot_key(t) in lost_slot)]
    unsold = [t for t in lost_tix if not t.get('soldout')]
    if unsold:
        hold.append((i, e.get('name') or '', [t['type'] for t in unsold]))
        continue
    old_start = {H.perf_key(t.get('type')): t.get('startDate') for t in old if t.get('startDate')}
    for t in new:
        if not t.get('startDate') and old_start.get(H.perf_key(t.get('type'))):
            t['startDate'] = old_start[H.perf_key(t.get('type'))]
    kn = {H.slot_key(t) for t in new}
    keep = [t for t in old if ((t.get('soldout') and (t.get('date') or '') >= TODAY)
            or ((t.get('url') or '') and 'pia.jp' not in (t.get('url') or ''))) and H.slot_key(t) not in kn]
    e['tickets'] = new + keep
    apply_ids.append(i)
    print('当てる id%-5s %s ｜取り直し %d枠＋残す %d枠（売り切れ %d）' % (
        i, (e.get('name') or '')[:26], len(new), len(keep), sum(1 for t in keep if t.get('soldout'))))
print('\n触らない（印の付いていない枠が消える）%d件:' % len(hold))
for i, n, ts in hold:
    print('  id%-5s %s ｜%s' % (i, n[:26], ' ／ '.join(ts)[:160]))
print('\n当てる %d件 ／ 触らない %d件' % (len(apply_ids), len(hold)))
io.open('tmp/heal_blocked_hold_1805.txt', 'w', encoding='utf-8').write(','.join(str(i) for i, _, _ in hold))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
