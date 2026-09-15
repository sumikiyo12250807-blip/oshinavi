# -*- coding: utf-8 -*-
"""ぴあで買える枠が0だった52件の「予定枚数終了（売り切れ）か販売終了か」を朝のために下調べする（読むだけ・2026-09-16 深夜）
・エントリの links.pia と各 ticket.url（ぴあのものだけ）を集め、tools/pia_statustext.py に1本ずつ渡す（間は道具の中で1.2秒）
・結果は tmp/zero52_status_0916.txt（エントリごとに「■ id 名前」の見出しをつける）
・index.html は書き換えない。印を付けるのは朝（DELETE_GATE 1.＝売り切れ・販売終了は消さずに印）
使い方: python zero52_status_0916.py
"""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
IDS = [1509, 1554, 2743, 3418, 3491, 3510, 3696, 4045, 4057, 4059, 4077, 4079, 4084, 4087, 4089, 4092, 4094, 4095,
       4100, 4106, 4111, 4116, 4117, 4121, 4259, 4333, 4373, 4392, 4396, 4401, 4410, 4418, 4420, 4809, 4820, 4951,
       5010, 5157, 5191, 5669, 5719, 6420, 6902, 6922, 7016, 7116, 7117, 7333, 7336, 7485, 7815, 9859]
src = io.open('index.html', encoding='utf-8').read()
by = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
out = []
for i in IDS:
    e = by.get(i)
    if not e:
        out.append('■ id%d（index.html に無い）\n' % i)
        continue
    urls = []
    for u in [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets') or []]:
        if isinstance(u, str) and 'pia.jp' in u and u not in urls:
            urls.append(u)
    r = subprocess.run([sys.executable, 'tools/pia_statustext.py', '--out', 'tmp/_z52_one.txt'] + urls, capture_output=True)
    body = io.open('tmp/_z52_one.txt', encoding='utf-8').read() if r.returncode == 0 else '取得できなかった（終了コード %d）\n' % r.returncode
    states = re.findall(r'^\s+\[([^\]]+)\] is-', body, re.M)
    out.append('■ id%d %s｜公演 %s｜状態 %s\n%s' % (i, e.get('name'), e.get('date'), ' / '.join(sorted(set(states))) or '（カードなし）', body))
    print('id%d %s' % (i, ' / '.join(sorted(set(states))) or '（カードなし）'), flush=True)
io.open('tmp/zero52_status_0916.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('done → tmp/zero52_status_0916.txt')
