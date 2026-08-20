# -*- coding: utf-8 -*-
"""再訂正：8/13投稿は本文にURLを貼っている（ユーザー明示「13日はリンク本文に貼ったよ ぜんぶ」）。
スマホの「ポストアクティビティ」画面はプロフィールアクセスまでで終わり、リンククリック欄が出ない。
＝**欄が見えない＝本文URL無し、ではない**（あたしの推論が誤り）。link は True に戻し、
link_cl は「モバイル画面では取得不能」として None のままにする。"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

P = 'tools/x_log.json'
d = json.load(open(P, encoding='utf-8'))
n = 0
for r in d['posts']:
    if r.get('posted') == '2026-08-13' and r.get('measured') == '2026-08-14':
        r['link'] = True
        r['link_cl'] = None
        r['note'] = (r['note'].split(' ／🚨訂正')[0]
                     + ' ／✅ユーザー明示「13日はリンク本文に貼ったよ ぜんぶ」＝本文URL型。'
                       'スマホのポストアクティビティ画面はプロフィールアクセスで終わりリンククリック欄が出ない'
                       '＝欄が見えないことは本文URL無しの証拠にならない（あたしの誤推論を訂正）。'
                       'リンククリック実数はPCのChromeで個別投稿を開いて取る')
        n += 1
        print('再訂正:', r['title'][:44], '→ link=True / link_cl=None(モバイルでは取れない)')
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('再訂正', n, '件')
