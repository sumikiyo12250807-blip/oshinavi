# -*- coding: utf-8 -*-
"""7882 パレイドリア・8145 WHITE JAM の会期から「もう終わった公演」を外す（2026-09-12 ユーザー決定）。
ユーザー「もう終わったイベントはけしていいよ」＝カードの日付の欄に、終わった公演の日は入れない。
（これから行われる公演は、売り切れ・受付終了でも入れる＝feedback_show_true_dates_not_sellable_range）
今朝あたしが終わった公演（8/9〜）まで広げてしまったのを、これからの公演の範囲に戻す。
使い方: python tmp/revert_past_0912.py [--apply]
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}


def setf(i, k, old, new):
    e = by[i]
    assert e.get(k) == old, 'id%s %s が想定と違う: %r' % (i, k, e.get(k))
    e[k] = new
    print('id%-5s %-10s %s\n             → %s' % (i, k, old, new))


setf(7882, 'dateLabel', '2026年8月9日(日)〜2026年9月27日(日) 東京・大阪・新潟・福岡',
     '2026年9月19日(土)〜2026年9月27日(日) 新潟・福岡')
setf(7882, 'venue', '全国ツアー（紀伊國屋ホール／サンケイホールブリーゼ／新潟県民会館 大ホール／J:COM北九州芸術劇場 大ホール）',
     '全国ツアー（新潟県民会館 大ホール／J:COM北九州芸術劇場 大ホール）')
setf(8145, 'dateLabel', '2026年8月9日(日)〜2026年12月9日(水) 北海道・神奈川・大阪・福岡・愛知',
     '2026年9月26日(土)〜2026年12月9日(水) 大阪・福岡・愛知')
setf(8145, 'venue', '全国ツアー（Zepp Sapporo／KT Zepp Yokohama／Zepp Namba（OSAKA）／Zepp Fukuoka／Zepp Nagoya）',
     '全国ツアー（Zepp Namba（OSAKA）／Zepp Fukuoka／Zepp Nagoya）')

if '--apply' not in sys.argv:
    print('\n(--apply で書き込み)')
    sys.exit(0)
open('index.html', 'w', encoding='utf-8').write(
    src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
print('書き込み完了')
