# -*- coding: utf-8 -*-
"""公演終了の削除候補を、別エージェントの独立検証に渡す形で書き出す（登録の締切や判定は出さない）。
id／公演名／会場／登録の公演日（dateLabel）／持っている全URL だけ。
使い方: python tmp/delcand_dump_0914.py <id,id,...>
出力: tmp/delcand_for_agent_0914.txt
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
IDS = [int(x) for x in sys.argv[1].split(',') if x.strip()]

src = open('index.html', encoding='utf-8').read()
m = re.search(r'  const EVENTS = (\[.*?\]);', src, re.S)
by = {e['id']: e for e in json.loads(m.group(1))}

out = []
for i in IDS:
    e = by.get(i)
    if not e:
        out.append('id=%s\t(エントリが無い)' % i)
        continue
    urls = []
    for k, u in (e.get('links') or {}).items():
        if isinstance(u, str) and u.startswith('http') and u not in urls:
            urls.append(u)
    for t in e.get('tickets') or []:
        u = t.get('url') or ''
        if u and u not in urls:
            urls.append(u)
    out.append('id=%s\t%s\t会場: %s\t表記: %s\n\t%s' % (
        i, e.get('name') or '', e.get('venue') or '', e.get('dateLabel') or '', '\n\t'.join(urls)))
open('tmp/delcand_for_agent_0914.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('%d件を書き出した → tmp/delcand_for_agent_0914.txt' % len(IDS))
