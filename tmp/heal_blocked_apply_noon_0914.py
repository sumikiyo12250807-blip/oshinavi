# -*- coding: utf-8 -*-
"""昼の「〆切日に発売時刻」ヒールで安全弁が止めた6件を、中身を見たうえで手で当てる（2026-09-14）。
止まった理由（tmp/heal_blocked_noon_0914.py で並べて確認）:
  5155・5332・5411・7326・8405＝同じ売り場なのに飛び先URLの書き方が違う（ticket.pia.jp/pia/event.do と t.pia.jp/pia/event/event.do）
    ＝安全弁が別の枠と数えた見かけ。取り直しの方には新しく出た先行もある（5155 大阪3/28・7326 大阪1/30・愛知1/31・石川11/23）。
  549 坂本冬美＝宮城9/19 は売り切れの印付きで出している枠。ぴあで買えないので取り直しに入らない＝売り切れは出し続ける。
当て方＝取り直した枠（tmp/heal_ids.json）に差し替え、元の枠のうち「売り切れの印付き（今日以降）」と「ぴあ以外」は残す。
取り直しに発売日が無い枠は、元の同じ公演の枠の startDate を引き継ぐ（heal の carry_start_dates と同じ考え）。
使い方: python tmp/heal_blocked_apply_noon_0914.py [--apply]
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
IDS = [549, 5155, 5332, 5411, 7326, 8405]
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
built = {o['id']: o for o in json.load(io.open('tmp/heal_ids.json', encoding='utf-8'))}


def perf(ty):
    mm = re.search(r'^(.*?（[^（）]*公演）)', ty or '')
    return mm.group(1) if mm else (ty or '')


for i in IDS:
    e, o = by[i], built[i]
    assert o.get('status') == 'convert', (i, o.get('status'))
    old = e.get('tickets') or []
    new = [dict(t) for t in o['tickets']]
    old_start = {perf(t.get('type')): t.get('startDate') for t in old if t.get('startDate')}
    for t in new:
        if not t.get('startDate') and old_start.get(perf(t.get('type'))):
            t['startDate'] = old_start[perf(t.get('type'))]
    keep = [t for t in old if (t.get('soldout') and (t.get('date') or '') >= TODAY)
            or ((t.get('url') or '') and 'pia.jp' not in (t.get('url') or ''))]
    e['tickets'] = new + keep
    print('id%-5s %s ｜取り直し %d枠＋残す %d枠（元 %d枠）' % (i, (e.get('name') or '')[:24], len(new), len(keep), len(old)))
    for t in keep:
        print('       残す %s' % t.get('type'))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
