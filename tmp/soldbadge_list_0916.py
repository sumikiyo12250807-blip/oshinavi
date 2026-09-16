# -*- coding: utf-8 -*-
"""買える枠0のエントリについて、ぴあの券種に「予定枚数終了」でこれからの公演日の行があれば、
tmp/x0916/soldbadge_add.py と同じ入力の形（1行1カード）で書き出す（読むだけ・2026-09-16 朝）。
すでに枠があるかどうかは soldbadge_add 側が見て、あるものは足さない。
ぴあの券種は tools/pia_tickets.py <URL> --all --json で読む（1.5秒あける・tmp/sb_cache_0916 に残す）。
使い方: python tmp/soldbadge_list_0916.py <ids ファイル>
出力: tmp/soldbadge_in_0916.txt
"""
import datetime
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
CACHE = 'tmp/sb_cache_0916'
os.makedirs(CACHE, exist_ok=True)
ids = {int(x) for x in re.findall(r'\d+', io.open(sys.argv[1], encoding='utf-8').read())}
src = io.open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}


def fetch(url):
    p = os.path.join(CACHE, hashlib.md5(url.encode()).hexdigest()[:12] + '.json')
    if os.path.exists(p):
        return json.load(io.open(p, encoding='utf-8'))
    out = subprocess.run([sys.executable, 'tools/pia_tickets.py', url, '--all', '--json'], capture_output=True)
    time.sleep(1.5)
    try:
        rows = json.loads(out.stdout.decode('utf-8', 'replace').strip())
    except Exception:
        print('  ❌ 読めなかった（混雑ページかも）: %s' % url)
        return None
    io.open(p, 'w', encoding='utf-8').write(json.dumps(rows, ensure_ascii=False, indent=1))
    return rows


lines, unread = [], 0
for i in sorted(ids):
    e = ev.get(i)
    if not e:
        continue
    urls = []
    for u in [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets') or []]:
        if u and 'pia.jp' in u and u not in urls:
            urls.append(u)
    for u in urls:
        rows = fetch(u)
        if rows is None:
            unread += 1
            continue
        for r in rows:
            if r.get('statustext') == '予定枚数終了' and (r.get('perfdate') or '') >= TODAY:
                lines.append('id%d 印なし: ぴあ「予定枚数終了」公演%s「%s」 %s' % (i, r['perfdate'], r.get('title') or '', u))
io.open('tmp/soldbadge_in_0916.txt', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('対象 %d件 → 予定枚数終了のこれからの行 %d（読めなかったページ %d）→ tmp/soldbadge_in_0916.txt' % (len(ids), len(lines), unread))
