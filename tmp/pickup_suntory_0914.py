# -*- coding: utf-8 -*-
"""主役②「サントリーホールの年末年始」の素材＝会場がサントリーホールで、公演が12月〜1月、
窓（9/14〜9/20）に発売が始まる枠を全部並べる（読むだけ）。出力: tmp/pickup_suntory_0914.txt"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
FROM, TO = '2026-09-14', '2026-09-20'
src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
o = io.open('tmp/pickup_suntory_0914.txt', 'w', encoding='utf-8')
for e in sorted(ev, key=lambda e: e.get('date') or ''):
    if 'サントリーホール' not in (e.get('venue') or '') + (e.get('name') or ''):
        continue
    if not ('2026-12-01' <= (e.get('date') or '') <= '2027-01-31'):
        continue
    ts = [t for t in e.get('tickets') or [] if FROM <= (t.get('startDate') or '') <= TO]
    if not ts:
        continue
    o.write('### id=%s %s\n   会期 : %s\n   会場 : %s\n' % (e['id'], e.get('name'), e.get('dateLabel'), e.get('venue')))
    for t in ts:
        o.write('     ・%s\n' % t['type'])
    o.write('\n')
o.close()
print(open('tmp/pickup_suntory_0914.txt', encoding='utf-8').read())
