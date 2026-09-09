# -*- coding: utf-8 -*-
"""振り分けたものを logs/assigned_YYYY-MM-DD.md に残す（公演名＋ジャンル＋URL）。

新着タブから出したぶんは、ユーザーが後から見る場所が無くなるので必ず記録を残す
（PLAYBOOK のゲートC＝「後から見られるリンクを残す」）。
直前のコミット（HEAD）と現物を突き合わせて、genre が "new" から変わったものを拾う。
"""
import datetime
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')


def load(text):
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', text, re.S)
    return {e['id']: e for e in json.loads(m.group(2))}


BASE = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'
old = load(subprocess.run(['git', 'show', BASE + ':index.html'],
                          capture_output=True).stdout.decode('utf-8', 'replace'))
new = load(open('index.html', encoding='utf-8').read())

rows = []
for i, e in old.items():
    if e.get('genre') != 'new' or i not in new:
        continue
    g = new[i].get('genre')
    if g and g != 'new':
        ls = new[i].get('links') or {}
        u = ls.get('pia') or ls.get('eplus') or ls.get('rakuten') or ls.get('lawson') or ''
        rows.append((i, new[i].get('name') or '', g, new[i].get('date') or '', u))

rows.sort(key=lambda r: (r[2], r[0]))
today = datetime.date.today().isoformat()
path = 'logs/assigned_%s.md' % today
with open(path, 'w', encoding='utf-8') as f:
    f.write('# %s に新着タブから振り分けたもの（%d件）\n\n' % (today, len(rows)))
    f.write('内訳＝朝にぴあ由来148件／そのあとユーザーが実物を見て確認した**ぴあ以外22件**（楽天20・e+2）。\n')
    f.write('別エージェントの独立チェック＝ぴあの区分との突合で149件中147件が対応表どおり、\n')
    f.write('ズレ2件は「海外ROCK・POPS×韓国→kpop」の例外＝正しい。\n')
    f.write('ぴあ以外22件も同じエージェントが売り場URLのカテゴリ階層と突き合わせて「ズレなし」。\n')
    f.write('id7498 は楽天のURLが /event/ だけでジャンルの手がかりが無く、ユーザーが musicetc と決めた。\n\n')
    f.write('新着タブに残してあるもの＝今日投入したぶん（翌朝の再チェックのあとで振り分ける）と、\n')
    f.write('id7558 Tommy february6（一般発売の枠がぴあから消えた＝実態が確かめられていない）。\n\n')
    cur = None
    for i, n, g, d, u in rows:
        if g != cur:
            cur = g
            f.write('\n## %s\n\n' % g)
        f.write('- id=%s %s（%s）\n' % (i, n, d))
        if u:
            f.write('  - %s\n' % u)
print('%d件を %s に残したわ' % (len(rows), path))
