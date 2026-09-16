# -*- coding: utf-8 -*-
"""朝のヒール（heal_stale_deadlines --apply）が 5717 一青窈のローチケ4枠を落とした＝HEAD から書き戻す（2026-09-16）。
落ちた枠＝抽選プレリク2次（宮崎 12/4・鹿児島 12/5）9/16 12:00発売／一般発売（宮崎・鹿児島）9/26 10:00発売（飛び先 l-tike.com）。
やり方＝HEAD の 5717 の枠のうち、飛び先が l-tike.com で今の登録に無いものを足す（ほかは触らない）。
使い方: python tmp/restore_5717_0916.py [--apply]
"""
import json
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
ID = 5717


def events(text):
    return json.loads(re.search(r'  const EVENTS = (\[.*?\]);', text, re.S).group(1))


head = next(e for e in events(subprocess.run(['git', 'show', 'HEAD:index.html'], capture_output=True).stdout.decode('utf-8')) if e['id'] == ID)
with open(P, encoding='utf-8', newline='') as f:
    text = f.read()
ev = events(text)
cur = next(e for e in ev if e['id'] == ID)
have = {(t.get('type'), t.get('url')) for t in cur['tickets']}
back = [t for t in head['tickets'] if 'l-tike.com' in (t.get('url') or '') and (t.get('type'), t.get('url')) not in have]
assert len(back) == 4, back
new_e = json.loads(json.dumps(cur, ensure_ascii=False))
new_e['tickets'] = sorted(new_e['tickets'] + back, key=lambda t: t.get('date') or '')
block = ['  ' + ln for ln in json.dumps(new_e, ensure_ascii=False, indent=2).split('\n')]

lines = text.split('\r\n')
out, i, hit = [], 0, 0
while i < len(lines):
    if lines[i] == '  {' and i + 1 < len(lines) and lines[i + 1] == '    "id": %d,' % ID:
        j = i
        while not lines[j].startswith('  }'):
            j += 1
        block[-1] += lines[j][3:]
        out += block
        hit += 1
        i = j + 1
        continue
    out.append(lines[i])
    i += 1
assert hit == 1
res = '\r\n'.join(out)
ev2 = events(res)
a = {x['id']: json.dumps(x, ensure_ascii=False, sort_keys=True) for x in ev2 if x['id'] != ID}
b = {x['id']: json.dumps(x, ensure_ascii=False, sort_keys=True) for x in ev if x['id'] != ID}
assert a == b and '\n' not in res.replace('\r\n', '')
print('5717 枠 %d → %d（ローチケ %d枠を戻す）' % (len(cur['tickets']), len(new_e['tickets']), len(back)))
for t in back:
    print('  ', t['type'])
if '--apply' in sys.argv:
    shutil.copyfile(P, 'index.html.bak_0916_restore5717')
    with open(P, 'w', encoding='utf-8', newline='') as f:
        f.write(res)
    print('書き込んだ')
