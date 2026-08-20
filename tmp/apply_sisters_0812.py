# -*- coding: utf-8 -*-
"""2605 ザ・シスターズハイ＝ぴあが単独公演URLを潰してツアーbundleに作り直したので貼り替える。
CRLFを壊さないようバイナリで読み書きし、該当エントリのJSONブロックだけを差し替える。"""
import io
import json
import os
import re
import shutil

P = 'index.html'
BK = 'index.html.bak_0812_sisters'

built = json.load(io.open('tmp/built_sisters_0812.json', encoding='utf-8'))[0]

raw = open(P, 'rb').read()
text = raw.decode('utf-8')

# 対象エントリの JSON オブジェクトを id で特定して範囲を取る
m = re.search(r'\n(\s*)\{\s*\r?\n\s*"id":\s*2605\b', text)
if not m:
    raise SystemExit('id=2605 のエントリが見つからない')
start = m.start(0) + 1
depth = 0
i = start
in_str = False
esc = False
while i < len(text):
    ch = text[i]
    if in_str:
        if esc:
            esc = False
        elif ch == '\\':
            esc = True
        elif ch == '"':
            in_str = False
    else:
        if ch == '"':
            in_str = True
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    i += 1
else:
    raise SystemExit('エントリの終端が見つからない')

old = json.loads(text[start:end])
print('--- 変更前 ---')
print(' venue:', old.get('venue'))
print(' pref :', old.get('prefecture'))
print(' date :', old.get('date'), '|', old.get('dateLabel'))
print(' pia  :', (old.get('links') or {}).get('pia'))
for t in old.get('tickets') or []:
    print('   -', t.get('type'))

new = dict(old)
for k in ('venue', 'prefecture', 'date', 'dateLabel', 'tickets'):
    new[k] = built.get(k)
links = dict(old.get('links') or {})
links['pia'] = (built.get('links') or {}).get('pia')
new['links'] = links
# 発売開始日は元エントリの実績を引き継ぐ（ぴあは受付中になると発売日を出さない）
for t in new['tickets']:
    if t.get('startDate') is None and t.get('type', '').startswith('一般発売'):
        t['startDate'] = '2026-08-12'
new['verified'] = True
new['verifiedAt'] = '2026-08-12'

indent = m.group(1)
body = json.dumps(new, ensure_ascii=False, indent=1)
body = '\n'.join((indent + ln if n else ln) for n, ln in enumerate(body.split('\n')))

print('--- 変更後 ---')
print(' venue:', new.get('venue'))
print(' pref :', new.get('prefecture'))
print(' date :', new.get('date'), '|', new.get('dateLabel'))
print(' pia  :', new['links'].get('pia'))
for t in new.get('tickets') or []:
    print('   -', t.get('type'), '| date=', t.get('date'), '| start=', t.get('startDate'))

out = text[:start] + body + text[end:]
# 元ファイルの改行コードを維持する（LF化するとsort_guardが誤ブロックする）
crlf_before = raw.count(b'\r\n')
shutil.copyfile(P, BK)
data = out.encode('utf-8')
open(P, 'wb').write(data)
crlf_after = open(P, 'rb').read().count(b'\r\n')
print('CRLF %d -> %d (backup: %s)' % (crlf_before, crlf_after, BK))
