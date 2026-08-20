# -*- coding: utf-8 -*-
"""肉チョモランマのX投稿(Fable版)を「今日」表記に直し、曜日と文字数を機械で検算する。
🚨文字数は目視で数えない（memory: project_sns_promotion）。"""
import datetime
import io

WD = '月火水木金土日'
for d in ['2026-08-04', '2026-08-29', '2026-09-02', '2026-07-04']:
    dt = datetime.date.fromisoformat(d)
    print('%s = %s曜' % (d, WD[dt.weekday()]))

src = io.open('tmp/x_post_0804_fable.txt', encoding='utf-8').read()
out = src.replace('明日8/4(火)19:00、', '今日8/4(火)19:00、')
assert out != src, '「明日8/4(火)19:00、」が見つからない'
io.open('tmp/x_post_0804_fable_final.txt', 'w', encoding='utf-8').write(out)

body = out.strip()
print('---')
print('総文字数(改行含む) = %d' % len(body))
print('本文のみ(URL/タグ/署名を除く) = %d'
      % len(body.split('https://oshinavi.jp')[0].strip()))
for k in ['8/29', '9/2', '3,500', 'Kアリーナ横浜', 'https://oshinavi.jp', '#肉チョモランマ']:
    print('%s 含む: %s' % (k, k in body))
