# 9/17 11:00〜14:30（UTC 02:00〜05:30）のユーザー発言を全部と、あたしの返事の要旨（先頭）を時刻順に出す
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
f = r'C:\Users\user\.claude\projects\C--Users-user-oshinavi\81f6fd91-937d-49b5-a1df-c78c18a54257.jsonl'
for ln in open(f, encoding='utf-8', errors='replace'):
    try:
        o = json.loads(ln)
    except Exception:
        continue
    ts = o.get('timestamp', '')
    if not ('2026-09-17T11:15' <= ts[:16] <= '2026-09-17T13:40'):
        continue
    c = o.get('message', {}).get('content')
    if isinstance(c, list):
        c = ' '.join(x.get('text', '') for x in c if isinstance(x, dict) and x.get('type') == 'text')
    if not isinstance(c, str) or not c.strip() or c.startswith('<'):
        continue
    who = 'U' if o.get('type') == 'user' else 'A'
    if who == 'A' and len(c) < 40:
        continue
    print(ts[11:16], who, '|', c.replace('\n', ' / ')[:700 if who == 'A' else 400])
    print()
