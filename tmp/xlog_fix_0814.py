# -*- coding: utf-8 -*-
"""8/13投稿2本の link 判定を訂正。
ユーザー確認＝BTOB投稿は「クリック数は4／この下にはもうスクロールできない」
＝**リンククリック欄そのものが存在しない**＝本文にURLが無い（セルフリプ型）。
memory feedback_x_ctr_observations ③「リンククリック数は本文にリンクを貼った投稿にしか計上されない」。"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

P = 'tools/x_log.json'
d = json.load(open(P, encoding='utf-8'))
n = 0
for r in d['posts']:
    if r.get('posted') == '2026-08-13' and r.get('measured') == '2026-08-14':
        r['link'] = False
        r['link_cl'] = None
        r['note'] = r['note'] + ' ／🚨訂正(ユーザー確認)=リンククリック欄が存在しない＝本文にURLが無いセルフリプ型だった。本命KPI(oshinavi.jpへの送客)はこの回も未計測'
        n += 1
        print('訂正:', r['title'][:44], '→ link=False')
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('訂正', n, '件')
