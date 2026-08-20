# -*- coding: utf-8 -*-
"""7/8 QC修正: 空カッコ会場3件の実会場埋め + プロセカ重複ticket集約。"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

# 2202 おいしくるメロンパン: 北海道限定2会場（全国ツアーではない）
e = byid[2202]
e['venue'] = 'CASINO DRIVE／ペニーレーン24'
e['dateLabel'] = '2026年11月6日(金)〜2026年11月7日(土) 北海道 CASINO DRIVE／ペニーレーン24'

# 2212 川野夏美／三丘翔太: 全国ツアー会場埋め
byid[2212]['venue'] = '全国ツアー（BLUES ALLEY JAPAN／Soap opera classics -Umeda-）'

# 2246 ヘタリア: 全国ツアー会場埋め（全角→半角）
byid[2246]['venue'] = '全国ツアー（日本青年館ホール／愛知県芸術劇場 大ホール／COOL JAPAN PARK OSAKA WWホール）'

# 2221 プロセカ: 同一文言ticketを集約
e = byid[2221]
seen, uniq = set(), []
for t in e['tickets']:
    k = (t['type'], t['date'])
    if k in seen:
        continue
    seen.add(k); uniq.append(t)
print('2221 tickets %d -> %d' % (len(e['tickets']), len(uniq)))
e['tickets'] = uniq

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html.bak_0708_qcfix', 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('QC修正 完了 (backup: index.html.bak_0708_qcfix)')
for i in [2202, 2212, 2246]:
    print('  id=%d venue=%s' % (i, byid[i]['venue']))
