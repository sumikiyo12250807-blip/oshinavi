# -*- coding: utf-8 -*-
"""index.html の1エントリを、build_pia_entries の出力で差し替える（CRLF維持）。
  使い方: python tmp/apply_entry_0812.py <built.json> <id> <backup_suffix>
差し替えるのは venue/prefecture/date/dateLabel/tickets/links.pia のみ
（[[feedback_harvest_today_sale_enddate]]＝venue/dateLabelの手修正を巻き戻さない、の逆で
 今回は会場自体が変わっているので意図的に上書きする）。"""
import io
import json
import re
import shutil
import sys

built_path, target_id, suffix = sys.argv[1], int(sys.argv[2]), sys.argv[3]
built = json.load(io.open(built_path, encoding='utf-8'))[0]

P = 'index.html'
BK = 'index.html.bak_' + suffix

raw = open(P, 'rb').read()
crlf_before = raw.count(b'\r\n')
lf_before = raw.count(b'\n')
if crlf_before != lf_before:
    raise SystemExit('元ファイルがCRLF統一でない（CRLF %d / LF %d）' % (crlf_before, lf_before))
text = raw.decode('utf-8').replace('\r\n', '\n')

m = re.search(r'\n(\s*)\{\s*\n\s*"id":\s*%d\b' % target_id, text)
if not m:
    raise SystemExit('id=%d のエントリが見つからない' % target_id)
start = m.start(0) + 1
depth = 0
i = start
in_str = esc = False
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
for k in ('venue', 'prefecture', 'date', 'dateLabel'):
    print(' %-11s %s' % (k, old.get(k)))
print(' pia         %s' % (old.get('links') or {}).get('pia'))
for t in old.get('tickets') or []:
    print('   - %s' % t.get('type'))

new = dict(old)
for k in ('venue', 'prefecture', 'date', 'dateLabel', 'tickets'):
    new[k] = built.get(k)
links = dict(old.get('links') or {})
links['pia'] = (built.get('links') or {}).get('pia')
new['links'] = links
new['verified'] = True
new['verifiedAt'] = '2026-08-12'

print('--- 変更後 ---')
for k in ('venue', 'prefecture', 'date', 'dateLabel'):
    print(' %-11s %s' % (k, new.get(k)))
print(' pia         %s' % new['links'].get('pia'))
for t in new.get('tickets') or []:
    print('   - %s | date=%s start=%s' % (t.get('type'), t.get('date'), t.get('startDate')))

indent = m.group(1)
body = json.dumps(new, ensure_ascii=False, indent=1)
body = '\n'.join((indent + ln if n else ln) for n, ln in enumerate(body.split('\n')))

out = (text[:start] + body + text[end:]).replace('\n', '\r\n')
shutil.copyfile(P, BK)
open(P, 'wb').write(out.encode('utf-8'))
r = open(P, 'rb').read()
print('CRLF %d -> %d / LF %d (backup: %s)' % (crlf_before, r.count(b'\r\n'), r.count(b'\n'), BK))
if r.count(b'\r\n') != r.count(b'\n'):
    raise SystemExit('🚨 CRLF統一が壊れた')
