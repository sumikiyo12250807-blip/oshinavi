# -*- coding: utf-8 -*-
"""reconcileが出した取りこぼし（id4502に発売前の先行枠が入っていない）を、
ぴあ機械パースの結果で枠を入れ直して直す。
[[feedback_capture_all_deadlines_on_add]]＝買える枠は1つ残らず載せる。
🚨CRLF保持（[[feedback_index_html_crlf_preserve]]）。

  python tmp/fix_4502_0817.py [--apply]
"""
import io, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
EID = 4502

fresh = {e['id']: e for e in json.load(io.open('tmp/entries_4502.json', encoding='utf-8'))}[EID]
src = io.open('index.html', encoding='utf-8', newline='').read()
before_crlf = src.count('\r\n')
BLOCK = re.compile(r'  \{\r\n    "id": (\d+),.*?\r\n  \},?', re.S)
m = {int(x.group(1)): x for x in BLOCK.finditer(src)}[EID]
cur = json.loads(m.group(0).rstrip(',').strip())

print('=== id%d %s ===' % (EID, cur.get('artist', '')[:50]))
print('登録されている枠 %d本:' % len(cur.get('tickets') or []))
for t in cur.get('tickets') or []:
    print('   %s | %s〜%s' % (t.get('type'), t.get('startDate'), t.get('date')))
print('ぴあ機械パースの枠 %d本:' % len(fresh.get('tickets') or []))
for t in fresh.get('tickets') or []:
    print('   %s | %s〜%s' % (t.get('type'), t.get('startDate'), t.get('date')))

cur['tickets'] = fresh['tickets']


def dump_entry(obj):
    body = json.dumps(obj, ensure_ascii=False, indent=2)
    body = '\n'.join(('  ' + ln) if ln else ln for ln in body.split('\n'))
    return body.replace('\n', '\r\n')


src = src[:m.start()] + dump_entry(cur) + (',' if m.group(0).endswith(',') else '') + src[m.end():]

EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S).group(2))
chk = [e for e in EV if e['id'] == EID][0]
print()
print('置換後の枠 %d本 / 総件数 %d' % (len(chk.get('tickets') or []), len(EV)))
print('CRLF %d → %d ／ LF単独 %d' % (before_crlf, src.count('\r\n'), src.count('\n') - src.count('\r\n')))

if APPLY:
    io.open('index.html.bak_0817_fix4502', 'w', encoding='utf-8', newline='').write(
        io.open('index.html', encoding='utf-8', newline='').read())
    io.open('index.html', 'w', encoding='utf-8', newline='').write(src)
    print('適用しました（backup: index.html.bak_0817_fix4502）')
else:
    print('（判定のみ。適用するなら --apply）')
