# -*- coding: utf-8 -*-
"""主役候補の中身を機械で吐く（9/13の記事の素材）。

窓＝2026-09-14〜2026-09-20 に発売が始まる枠だけを、券種名・発売日時・締切つきで出す。
🚨記事の数字は「書いた記憶」でなく登録データを数える（[[feedback_article_factcheck_before_publish]]）
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

FROM, TO = '2026-09-14', '2026-09-20'

IDS = [7324, 6988, 5212, 3406, 4293, 4845, 4850, 4771, 4772, 4775, 7576, 7572,
       4802, 3568, 4898, 1, 2159, 729, 4490, 4538, 4118, 5526, 5201, 4793,
       1109, 1055, 523, 5717, 549, 1634, 3477, 6138, 3251, 4350, 2239]

h = io.open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
by_id = {e['id']: e for e in EVENTS}

out = io.open('tmp/pickup_cand_0914.txt', 'w', encoding='utf-8')
w = out.write

for i in IDS:
    e = by_id.get(i)
    if not e:
        w('## id=%d ← **エントリが無い**\n\n' % i)
        continue
    w('## id=%d %s [%s]\n' % (i, e.get('artist') or e.get('name'), e.get('genre')))
    if (e.get('name') or '') != (e.get('artist') or ''):
        w('   公演名 : %s\n' % e.get('name'))
    w('   会期   : %s（date=%s）\n' % (e.get('dateLabel'), e.get('date')))
    w('   会場   : %s\n' % e.get('venue'))
    w('   都道府県: %s\n' % e.get('prefecture'))
    for k in ('url', 'officialUrl'):
        if e.get(k):
            w('   %-7s: %s\n' % (k, e[k]))
    links = e.get('links') or {}
    for k, v in links.items():
        w('   link.%-4s: %s\n' % (k, v))
    tk = e.get('tickets') or []
    w('   枠 全%d件（うち窓内 %d件）\n'
      % (len(tk), sum(1 for t in tk
                      if t.get('startDate') and FROM <= t['startDate'] <= TO)))
    for t in tk:
        inwin = t.get('startDate') and FROM <= t['startDate'] <= TO
        w('     %s %-28s 発売=%s %s / 締切=%s / %s%s\n'
          % ('★' if inwin else '  ',
             (t.get('type') or '')[:28],
             t.get('startDate'), t.get('startTime') or '',
             t.get('date'), t.get('dateLabel') or '',
             ' [予定枚数終了]' if t.get('soldout') else ''))
        if t.get('url'):
            w('        %s\n' % t['url'])
    w('\n')

out.close()
print('→ tmp/pickup_cand_0914.txt / %d件' % len(IDS))
