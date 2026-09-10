# -*- coding: utf-8 -*-
"""昼のヒールのあとも「本日発売のまま締切が入っていない」11件が、
ヒールの対象に入っていたのか／なぜ残ったのかを見る。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = '2026-09-10'

h = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))

build = io.open('tmp/heal_build_0910.txt', encoding='utf-8').read()
heal_ids = {}
for m in re.finditer(r'\[\d+/\d+\] (\d+) (.+)', build):
    heal_ids[int(m.group(1))] = m.group(2).strip()

NAMES = ['沢田研二', 'JUNICHI INAGAKI', '春風亭一之輔', '林家希林', '日本フィルハーモニー交響楽団',
         'オズブラ', '国立能楽堂', 'ホーム スイート ホーム', 'GirlPoP', 'パーカーズ']

for nm in NAMES:
    for e in ev:
        name = (e.get('name') or '')
        if nm not in name:
            continue
        hit = [t for t in (e.get('tickets') or [])
               if t.get('startDate') == TODAY and (e.get('date') or '') > TODAY
               and not t.get('soldout')]
        if not hit:
            continue
        st = heal_ids.get(e['id'], '（ヒールの対象に入っていない）')
        print('id%-5d %-34s' % (e['id'], name[:34]))
        print('     ヒール: %s' % st)
        for t in hit:
            print('     枠   : %-46s date=%s' % ((t.get('type') or '')[:46], t.get('date')))
        print('     links: %s' % {k: (v[:60] if isinstance(v, str) else v)
                                  for k, v in (e.get('links') or {}).items() if v})
        print()
        break
