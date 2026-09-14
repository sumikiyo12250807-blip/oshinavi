# -*- coding: utf-8 -*-
"""9/14夜の照合（tmp/x0914/reconcile_audit_0914.txt）で出た2件を直す。改行は CRLF を保つ。
  2500 ドラクエ ウインドオーケストラ（東京国際フォーラム 12/30〜）＝4次プリセール【単日券】【通し券】〜9/14 23:59 に
       今朝の独立検証で売り切れの印を付けたが、ぴあ eventCd=2627834 は今「受付中 ～2026/9/14(月) 23:59」（18:1x に pia_tickets で確認）
       → 売り切れの印を外す（買えるのに売り切れと出すと嘘になる）
  5732 SION'S SQUAD「一般発売（東京 12/4公演）10/3 10:00発売」＝飛び先が京都・大阪の公演のページ eventCd=2634827 だった
       → 12/4 新宿LOFT が載っているページ eventCd=2634453（発売前 2026/10/3 10:00）に直す
使い方: python tmp/x0914/fix_2500_5732.py [--apply]
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}

hit = [t for t in by[2500]['tickets'] if t['type'].startswith('4次プリセール') and '2627834' in (t.get('url') or '')]
assert len(hit) == 2 and all(t.get('soldout') for t in hit), [t['type'] for t in hit]
for t in hit:
    t.pop('soldout', None)
    t.pop('soldoutSince', None)
    print('2500 売り切れの印を外す: %s' % t['type'])

hit = [t for t in by[5732]['tickets'] if t['type'] == '一般発売（東京 12/4公演）10/3 10:00発売']
assert len(hit) == 1 and '2634827' in (hit[0].get('url') or ''), hit
print('5732 飛び先 %s → https://t.pia.jp/pia/event/event.do?eventCd=2634453' % hit[0]['url'])
hit[0]['url'] = 'https://t.pia.jp/pia/event/event.do?eventCd=2634453'

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
