# -*- coding: utf-8 -*-
"""ぴあ実ページの枠を機械パースして、会場・県・公演日を一覧で出す（dateLabel作成の根拠用）。"""
import json, subprocess, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
url = sys.argv[1]
r = subprocess.run([sys.executable, 'tools/pia_tickets.py', url, '--all', '--json'], capture_output=True)
rows = json.loads(r.stdout.decode('utf-8', 'replace'))
print('%d枠' % len(rows))
for x in rows:
    print(' | '.join(str(x.get(k)) for k in ('state', 'name', 'venue', 'pref', 'when', 'showdate', 'statustext')))
