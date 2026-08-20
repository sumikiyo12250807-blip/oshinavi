# -*- coding: utf-8 -*-
"""食い違いが出た数件を、登録tickets と ぴあ全券種を1対1で並べて目視できる形に出す。"""
import json
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
IDS = [3508, 3471, 3477, 3509, 3513]

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

out = []
for i in IDS:
    e = byid[i]
    out.append(f"===== id={i}  {e.get('artist')} =====")
    out.append(f"  venue={e.get('venue')}")
    out.append(f"  date={e.get('date')}  dateLabel={e.get('dateLabel')}")
    out.append('  --- 登録tickets ---')
    for t in e.get('tickets') or []:
        out.append(f"    {t.get('type')}")
        out.append(f"        date={t.get('date')} start={t.get('startDate')} url={(t.get('url') or '-')[:74]}")
    cds = []
    for c in re.findall(r'event(?:Bundle)?Cd=(\w+)', json.dumps(e, ensure_ascii=False)):
        if c not in cds:
            cds.append(c)
    for cd in cds:
        out.append(f'  --- ぴあ全券種（受付終了も含む） cd={cd} ---')
        r = subprocess.run([sys.executable, 'tools/pia_tickets.py', cd, '--all', '--json'],
                           capture_output=True, timeout=180)
        if r.returncode != 0:
            out.append('    取得失敗 ' + (r.stderr or b'').decode('utf-8', 'replace')[:150])
            continue
        for g in json.loads(r.stdout.decode('utf-8')):
            out.append(f"    [{g['state']}] {g['title'][:78]}")
            out.append(f"        when={g['when']} / 公演{g['perfdate']}〜{g['perf_end']} / {g['pref']} {g['venue'][:28]}")
        time.sleep(1.2)
    out.append('')

open('tmp/deep_new_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/deep_new_0730.txt')
