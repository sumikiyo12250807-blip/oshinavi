# -*- coding: utf-8 -*-
"""枠1つだけに売り切れの印を付ける（2026-09-14 朝）。消さない＝soldout:true ＋ soldoutSince（DELETE_GATE 1.）。
tools/mark_soldout.py はエントリ単位で「ぴあに買える枠があるか」を見るので、同じエントリの中で1会場だけ売り切れた型を拾えない。
根拠＝ぴあの生HTMLの状態の文字:
  id8347 あつこ&タニケン 東京12/12 世田谷区・烏山区民会館 先行受付(先着順) … eventCd=2636166 rlsCd=003 で「予定枚数終了」
  （別エージェントの再導出で見つかり、tools/pia_statustext.py で読み直した＝tmp/statustext_8347_0914.txt）
使い方: python tmp/mark_ticket_soldout_0914.py [--apply]
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
TARGETS = [(8347, '先行受付（先着順）（東京 12/12公演）')]

src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
n = 0
for i, key in TARGETS:
    hit = [t for t in by[i]['tickets'] if key in (t.get('type') or '') and not t.get('soldout')]
    print('id%s %s → 当たる枠 %d' % (i, key, len(hit)))
    for t in hit:
        print('   %s | date=%s' % (t['type'], t.get('date')))
        t['soldout'] = True
        t['soldoutSince'] = TODAY
        n += 1
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
body = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
io.open('index.html', 'w', encoding='utf-8', newline='').write(src[:m.start()] + m.group(1) + body + m.group(3) + src[m.end():])
print('書き込み完了 %d枠' % n)
