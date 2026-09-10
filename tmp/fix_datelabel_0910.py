# -*- coding: utf-8 -*-
"""会期(date/dateLabel)と会場(venue)を、**和集合**で直す。

🚨ビルド結果で上書きしない＝ビルドは「今買える枠」しか見ないので初日が縮む
   （[[feedback_show_true_dates_not_sellable_range]]＝事実の会期で書く）。
🚨CRLFを壊さない（[[feedback_index_html_crlf_preserve]]）＝newline="" で読み書きする。

使い方: python tmp/fix_datelabel_0910.py [--apply]
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv

# id: {直すフィールド: 新しい値}
FIX = {
    # 千秋楽が三重 2027/1/23 まであるのに date が 1/17 で止まっていて、
    # 1/17を過ぎた瞬間にカードが画面から消える（reconcile の QC-EVDATE）。
    # 初日 11/7 はそのまま＝縮めない。
    2159: {
        'date': '2027-01-23',
        'dateLabel': '2026年11月7日(土)〜2027年1月23日(土) 全国ツアー',
    },
    # GENERATIONS LIVE TOUR 2026 "PARALLEL QUEST" は 8会場12公演。
    # うち今も買えるのは 福岡11/3・静岡12/11・東京12/22 の3公演（公式＋ローチケで確認）。
    # 福岡11/3 を足したので会期の初日を 11/3 に伸ばし、会場にも足す。
    3568: {
        'dateLabel': '2026年11月3日(火)〜2026年12月22日(火) 全国ツアー',
        'venue': '全国ツアー（マリンメッセ福岡A館／静岡 エコパアリーナ／国立代々木競技場 第一体育館）',
    },
}

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))

for e in events:
    f = FIX.get(e['id'])
    if not f:
        continue
    print('## id=%d %s' % (e['id'], e.get('artist') or e.get('name')))
    for k, v in f.items():
        print('   %-9s %s' % (k, e.get(k)))
        print('   %-9s → %s' % ('', v))
        e[k] = v
    print()

if APPLY:
    # 🚨書き戻しの形は refresh_deadlines_0909.py と1文字も変えない
    #   （indent=2 ＋ 改行をCRLFに戻す）。ここを変えると全行が差分になる
    body = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n')
    out = h[:m.start(2)] + body + h[m.end(2):]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
    print('書き込み完了')
else:
    print('(--apply で書き込み)')
