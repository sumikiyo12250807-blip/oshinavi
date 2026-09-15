# -*- coding: utf-8 -*-
"""push 前の独立の読み直し（別エージェント・夜のヒールの36件をぴあの実物で照合）の指摘のうち、画面が事実と違う4件を直す（2026-09-15夜）。
  4164 島袋寛子＝福岡10/9（eventCd=2628973）・愛知10/30（2631134）が 8/31 に付けた「売り切れ」のままだが、ぴあは販売期間中
        （福岡〜9/30 23:59・愛知〜10/21 23:59）→ 締切を入れて売り切れの印を外す。大阪10/4 は売り切れのまま
  3853 阪神×広島 9/17＝[01]「ビジター専用応援席／一般発売 〜9/17 14:00」（売り切れの印）は [00]（「/」が半角なだけ・同じURL）と同じ枠で、
        ぴあは販売期間中 → 印の付いた二重の方を外す（飛び先が同じなので畳んでよい＝feedback_dedup_badges_keeps_urls の条件外）
  4293 東京フィル第九＝[02] 東京12/19 一般発売（eventCd=2626567）がぴあで予定枚数終了 → 売り切れの印
  4489 ASKA＝[12] 熊本12/26 紙チケット（eventCd=2626038）がぴあで予定枚数終了（電子は販売中）→ 紙だけ売り切れの印
直さない（残す）＝二重の3件（2500・3370・3997＝飛び先URLが違うので畳まない決まり）／今日で消える3件（1722・4293の古い形・7945）
改行は CRLF を保つ。使い方: python tmp/x0916/fix_verify_0915eve.py [--apply]
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
TODAY = '2026-09-15'

src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
byid = {e['id']: e for e in events}


def one(e, pred, what):
    hit = [t for t in e['tickets'] if pred(t)]
    assert len(hit) == 1, 'id%s %s が %d 枠' % (e['id'], what, len(hit))
    return hit[0]


e = byid[4164]
for pref, show, dl, ddate in (('福岡', '10/9', '9/30 23:59', '2026-09-30'), ('愛知', '10/30', '10/21 23:59', '2026-10-21')):
    t = one(e, lambda t: t['type'].startswith('一般発売（%s %s公演）' % (pref, show)), pref)
    old = t['type']
    t['type'] = '一般発売（%s %s公演）〜%s' % (pref, show, dl)
    t['date'] = ddate
    t.pop('soldout', None)
    t.pop('soldoutSince', None)
    print('  4164 %s → %s（売り切れの印を外した）' % (old, t['type']))

e = byid[3853]
t = one(e, lambda t: t['type'] == 'ビジター専用応援席／一般発売（兵庫 9/17公演）〜9/17 14:00' and t.get('soldout'), '全角スラッシュの二重')
keep = one(e, lambda t: t['type'] == 'ビジター専用応援席/一般発売（兵庫 9/17公演）〜9/17 14:00', '半角スラッシュの枠')
assert keep.get('url') == t.get('url'), '飛び先が違う＝畳まない'
e['tickets'].remove(t)
print('  3853 二重の「ビジター専用応援席／…」（売り切れの印）を外した → 枠%d' % len(e['tickets']))

e = byid[4293]
t = one(e, lambda t: t['type'] == '一般発売（東京 12/19公演）〜12/16 23:59', '東京12/19')
t['soldout'] = True
t['soldoutSince'] = TODAY
print('  4293 %s → 予定枚数終了の印' % t['type'])

e = byid[4489]
t = one(e, lambda t: t['type'] == '一般発売（紙チケット）（熊本 12/26公演）〜11/18 23:59', '熊本 紙')
t['soldout'] = True
t['soldoutSince'] = TODAY
print('  4489 %s → 予定枚数終了の印' % t['type'])

if not APPLY:
    print('（--apply で書き込み）')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
