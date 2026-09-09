# -*- coding: utf-8 -*-
"""ビルド結果のうち「既存に無い公演の枠」だけを足す（券種名の違いで二重登録しない）。

  python tmp/add_missing_slots_0910.py <built.json> [--apply]

🚨券種名（骨格）で突き合わせると二重登録になる＝ぴあは同じ枠を
   「一般発売（茨城 10/31公演）」と「一般発売【ノバホール公演】（茨城 10/31公演）」の
   両方の書き方で出すことがある（2026-09-10 id942 キーウで発生・未適用で気づいた）。
   → **（県・公演日・締切）**で突き合わせる。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
SRC = sys.argv[1]
APPLY = '--apply' in sys.argv


def key(t):
    m = re.search(r'（([^（）]*?)\s*((?:R\d+年\s*)?[\d/〜]+)(?:\s+\d{1,2}:\d{2})?公演）', t.get('type') or '')
    if not m:
        return (t.get('type'), '', t.get('date'))
    return (m.group(1).strip(), re.sub(r'R\d+年\s*', '', m.group(2)).strip(), t.get('date'))


src = io.open('index.html', encoding='utf-8').read()
mm = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(mm.group(2))
by = {e['id']: e for e in events}

built = json.load(io.open(SRC, encoding='utf-8'))
added = 0
for b in built:
    e = by.get(b['id'])
    if not e:
        continue
    have = {key(t) for t in (e.get('tickets') or [])}
    myurl = (e.get('links') or {}).get('pia') or ''
    for bt in b.get('tickets') or []:
        if key(bt) in have:
            continue
        t = dict(bt)
        if not t.get('url') and myurl:
            t['url'] = myurl
        e.setdefault('tickets', []).append(t)
        have.add(key(bt))
        added += 1
        print('  id=%-5s ＋%s' % (e['id'], t['type'][:70]))

print('\n足した枠 %d' % added)
if not APPLY:
    print('(--apply で書き込み)')
    sys.exit(0)
arr = json.dumps(events, ensure_ascii=False, indent=2)
io.open('index.html', 'w', encoding='utf-8').write(
    src[:mm.start()] + mm.group(1) + arr + mm.group(3) + src[mm.end():])
print('書き込み完了')
