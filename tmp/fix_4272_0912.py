# -*- coding: utf-8 -*-
"""id4272 横浜DeNAベイスターズ対阪神タイガース／公式戦 から、延期になった「一般販売（神奈川 10/4公演）9/13 12:00発売」の枠を外す（2026-09-12夜）。
根拠＝球団の告知「2026年 チケット第8回販売［対象試合：10/4(日)］の見合わせについて」（9/11・https://www.baystars.co.jp/news/2026/09/0911_07.php）
      ＋ぴあの生HTML（eventCd=2636326）の状態の文字「後日、販売を予定しております」（tmp/x0913/statustext_4272_0912.txt）。
新しい発売日は球団の発表待ち＝決まったら取り直す（嘘の発売日を残さない＝memory feedback_no_fake_info）。
エントリは消さない（10/4の試合は行われる。ほかの試合の枠もある）。
使い方: python tmp/fix_4272_0912.py [--apply]
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
KEY = '一般販売（神奈川 10/4公演）9/13 12:00発売'
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 4272)
before = len(e['tickets'])
hit = [t for t in e['tickets'] if t.get('type') == KEY]
print('id4272 %s | 枠 %d本 | 外す枠 %d本' % (e['name'], before, len(hit)))
for t in e['tickets']:
    print('   %s %s | date=%s' % ('✂' if t in hit else ' ', t.get('type'), t.get('date')))
if len(hit) != 1:
    print('当たりが1本でないので止める')
    sys.exit(2)
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
e['tickets'] = [t for t in e['tickets'] if t is not hit[0]]
nl = '\r\n' if '\r\n' in src else '\n'
body = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
io.open('index.html', 'w', encoding='utf-8', newline='').write(src[:m.start()] + m.group(1) + body + m.group(3) + src[m.end():])
print('書き込み完了（%d本 → %d本）' % (before, len(e['tickets'])))
