# -*- coding: utf-8 -*-
"""id7326 35.7＝会期がぴあで買える3〜4公演の範囲（11/13〜12/5）に縮んでいたのを、公式ツアーの事実の会期に直す（2026-09-14）。
根拠＝公式 sanjugotennana.com/live/ の生HTML（tmp/fetch_357_live_0914.py・要約を通さない）
「35.7 ONEMAN LIVE TOUR 2026-2027」10公演：
  11/05 埼玉 HEAVEN'S ROCK さいたま新都心 VJ-3 ／11/13 北海道 cube garden ／11/15 宮城 darwin ／11/21 広島 SECOND CRUTCH
  11/23 石川 金沢AZ ／12/04 福岡 DRUM Be-1 ／12/05 香川 高松DIME ／R9 1/30 大阪 BIGCAT ／1/31 愛知 NAGOYA CLUB QUATTRO
  2/11 東京 EX THEATER ROPPONGI
会期は事実で書く＝買える範囲に縮めない（feedback_show_true_dates_not_sellable_range）。5県以上は「全国」。
枠（tickets）は触らない＝ぴあで買えるのはまだ北海道・宮城・広島・香川だけ。
使い方: python tmp/fix_7326_0914.py [--apply]
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 7326)
assert e['date'] == '2026-12-05', e['date']
new = {
    'date': '2027-02-11',
    'dateLabel': '2026年11月5日(木)〜2027年2月11日(木) 全国',
    'prefecture': '全国',
    'venue': "全国ツアー（HEAVEN'S ROCK さいたま新都心 VJ-3／cube garden／darwin／SECOND CRUTCH／金沢AZ／"
             "DRUM Be-1／高松DIME／BIGCAT／NAGOYA CLUB QUATTRO／EX THEATER ROPPONGI）",
}
for k, v in new.items():
    print('%-10s %s\n        → %s' % (k, e.get(k), v))
    e[k] = v
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
