# -*- coding: utf-8 -*-
"""楽天の発売前ハーベスト（tmp/rakuten_presale.json の presale）が、うちに登録済みかを当てる（読むだけ・2026-09-14）。
判定＝楽天の公演コード（URL末尾の /rtXXXX/）が index.html のどこかに出てくるか（Deep Link は murl にエンコードされて入る）。
登録済みなら、そのエントリに「発売前の枠」が入っているか（startDate が今日より後の枠）も見る＝
既存への足し込み漏れ（9/10 理芽・KOKO・春猿火の型）を拾うため。
使い方: python tmp/rakuten_presale_check_0914.py
出力: tmp/rakuten_presale_check_0914.txt
"""
import datetime
import io
import json
import re
import sys
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
pre = json.load(io.open('tmp/rakuten_presale.json', encoding='utf-8'))['presale']
src = io.open('index.html', encoding='utf-8').read()
dec = urllib.parse.unquote(src)
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))

out = ['楽天の発売前 %d件' % len(pre)]
for p in pre:
    code = re.search(r'/(rt[0-9a-z]+)/?$', p['url'])
    code = code.group(1) if code else ''
    hits = []
    for e in ev:
        blob = urllib.parse.unquote(json.dumps(e, ensure_ascii=False))
        if code and ('/%s/' % code) in blob:
            hits.append(e)
    wins = ' ／ '.join('%s %s' % (w.get('type'), w.get('timming')) for w in p.get('presale_windows') or [])
    if not hits:
        out.append('🆕 未登録 | %s | 公演 %s〜%s | %s | %s' % (p['name'][:50], p.get('first'), p.get('last'), wins, p['url']))
        continue
    for e in hits:
        fut = [t for t in e.get('tickets') or [] if (t.get('startDate') or '') > TODAY]
        mark = '✅ 発売前の枠あり' if fut else '⚠️ 登録済みだが発売前の枠が無い'
        out.append('%s | id%s %s | %s | %s' % (mark, e['id'], (e.get('name') or '')[:40], wins, p['url']))
        for t in fut:
            out.append('        登録の発売前: %s | start=%s date=%s' % (t.get('type'), t.get('startDate'), t.get('date')))
io.open('tmp/rakuten_presale_check_0914.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
