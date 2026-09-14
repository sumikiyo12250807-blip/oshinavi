# -*- coding: utf-8 -*-
"""push前の照合（reconcile_pia --ids・21:33）で出た引っかかりを、ぴあの生の行で確かめる（2026-09-14 夜）。
id ごとに、登録の枠と、ぴあの全券種（状態・文言・会場・締切・券種名）を並べる。
最後に「これから行われる公演のいちばん遅い日」（span_rows と同じ決まり＝終わった・中止・延期は外す）も出す。
ぴあは1件ずつ（照合と合わせて同時2本まで）。書き込みはしない。
使い方: python tmp/raw_rows_2133_0914.py 2127,3875,7165,5044   → tmp/raw_rows_2133_0914.md
"""
import datetime
import io
import json
import re
import subprocess
import sys
import time

sys.path.insert(0, 'tools')
import heal_stale_deadlines as H

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
src = io.open('index.html', encoding='utf-8').read()
by = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
out = []
for i in [int(x) for x in sys.argv[1].split(',')]:
    e = by[i]
    out.append('## id%s %s ｜date %s ｜%s' % (i, e.get('name'), e.get('date'), e.get('dateLabel')))
    out.append('登録:')
    for t in e.get('tickets') or []:
        out.append('  ・%s ｜締切 %s｜発売 %s｜%s%s' % (t.get('type'), t.get('date'), t.get('startDate') or '-',
                   H._url_id(t.get('url')), '｜売り切れ' if t.get('soldout') else ''))
    last = ''
    for u in H.pia_urls(e):
        time.sleep(1.5)
        r = subprocess.run([sys.executable, 'tools/pia_tickets.py', u, '--all', '--json'], capture_output=True)
        try:
            rows = json.loads(r.stdout.decode('utf-8', 'replace'))
        except json.JSONDecodeError:
            out.append('ぴあ %s ＝読めない' % H._url_id(u))
            continue
        out.append('ぴあ %s（%d行）:' % (H._url_id(u), len(rows)))
        for x in rows:
            out.append('  ・[%s] %s〜%s %s %s ｜%s ｜%s ｜%s' % (
                x['state'], x['perfdate'], x['perf_end'], x['pref'], x['venue'], x['statustext'], x['when'], x['title'][:40]))
            end = x.get('perf_end') or x.get('perfdate') or ''
            if end >= TODAY and not re.search(r'(中止|延期)', x.get('statustext') or '') and end > last:
                last = end
    out.append('→ これから行われる公演のいちばん遅い日＝%s\n' % (last or '（分からない）'))
    print('id%s 済' % i)
io.open('tmp/raw_rows_2133_0914.md', 'w', encoding='utf-8').write('\n'.join(out))
print('書き出し tmp/raw_rows_2133_0914.md')
