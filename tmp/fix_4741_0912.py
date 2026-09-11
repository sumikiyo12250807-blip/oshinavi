# -*- coding: utf-8 -*-
"""id4741 大江千里の会期に、同じツアーの福岡 2027/1/22 を入れる（2026-09-12 朝）。
根拠＝ぴあの生ページ（tmp/oe_b2670658.txt）: まとめページ b2670658「大江千里トリオ」に
  2027-01-22 福岡市民ホール 中ホール（プレリザーブ受付終了）／2027-01-23〜24 京都・兵庫（一般発売 9/12 10:00）
今日のスイープで拾った 8264（同じまとめページ）は 4741 と同じ一般発売1枠しか持たない＝二重登録なので入れない。
会期はこれから行われる公演を入れる（feedback_show_true_dates_not_sellable_range）。prefecture は買える京都・兵庫のまま。
使い方: python tmp/fix_4741_0912.py [--apply]
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 4741)
OLD_L = '2027年1月23日(土)〜2027年1月24日(日) 京都・兵庫'
OLD_V = '全国ツアー（京都コンサートホール 小ホール／兵庫県立芸術文化センター 阪急 中ホール）'
assert e.get('dateLabel') == OLD_L and e.get('venue') == OLD_V, '4741 が想定と違う: %r / %r' % (e.get('dateLabel'), e.get('venue'))
e['dateLabel'] = '2027年1月22日(金)〜2027年1月24日(日) 福岡・京都・兵庫'
e['venue'] = '全国ツアー（福岡市民ホール 中ホール／京都コンサートホール 小ホール／兵庫県立芸術文化センター 阪急 中ホール）'
print('id4741 dateLabel %s\n              → %s' % (OLD_L, e['dateLabel']))
print('id4741 venue     %s\n              → %s' % (OLD_V, e['venue']))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
open('index.html', 'w', encoding='utf-8').write(
    src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
print('書き込み完了')
