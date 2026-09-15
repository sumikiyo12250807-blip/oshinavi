# -*- coding: utf-8 -*-
"""7324 ヨーヨー・マ サントリーホール40周年スペシャルコンサート＝本公演 10/25・10/27 の一般発売が、ぴあで「予定枚数終了」（2026-09-15夜）。
根拠＝tools/pia_tickets.py b2669025 --all --json の statustext（tmp/x0916/pt_7324.json）
  10/25 一般発売 eventCd=2622990 rlsCd=001「予定枚数終了」／10/27 一般発売 eventCd=2622991 rlsCd=001「予定枚数終了」
登録は追加公演 10/28 の2枠だけ＝本公演を売り切れの印付きで足す（売り切れは消さずに出す＝feedback_soldout_keep_visible）。
会期も事実どおり 10/25〜10/28 に（date は最終公演日 10/28 のまま）。売り切れ枠の date は締切が出ていないので公演日。改行は CRLF を保つ。
使い方: python tmp/x0916/fix_7324_yoyoma.py [--apply]
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = '2026-09-15'
ADD = [
    ('一般発売（東京 10/25公演）', '2026-10-25', 'https://t.pia.jp/pia/event/event.do?eventCd=2622990'),
    ('一般発売（東京 10/27公演）', '2026-10-27', 'https://t.pia.jp/pia/event/event.do?eventCd=2622991'),
]
src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 7324)
have = {t['type'] for t in e['tickets']}
for typ, d, u in ADD:
    if typ in have:
        print('  もうある: %s' % typ)
        continue
    e['tickets'].append({'type': typ, 'date': d, 'url': u, 'soldout': True, 'soldoutSince': TODAY})
    print('  ＋ %s（予定枚数終了）' % typ)
old = e['dateLabel']
e['dateLabel'] = '2026年10月25日(日)〜2026年10月28日(水) 東京 サントリーホール 大ホール'
print('  会期: %s → %s' % (old, e['dateLabel']))
if '--apply' not in sys.argv:
    print('（--apply で書き込み）')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
