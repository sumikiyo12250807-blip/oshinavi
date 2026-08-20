# -*- coding: utf-8 -*-
"""id4448 の2本目の販売枠（eventCd=2629201）を復元する。

経緯＝4476 を 4448 に統合したとき2枠とも残したが、直後に dedup_badges を流したため
「表示フィールドが完全一致＝重複」と判定されて畳まれ、**まだぴあで販売中の売り場が
サイトから消えた**（独立検証で発覚）。買える枠は1つ残らず載せるのが方針
（[[feedback_capture_all_deadlines_on_add]]）。迷った状態で消さない（[[feedback_user_confirms_expired]]）。

⚠️このままでは次に dedup_badges を流すとまた畳まれる。1部/2部の時刻が分かるまでの
   暫定復元であることを plan.md と logs に残す。

🚨CRLF保持（[[feedback_index_html_crlf_preserve]]）。

  python tmp/restore_4448_slot_0817.py [--apply]
"""
import io, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
EID = 4448
URL2 = 'https://t.pia.jp/pia/event/event.do?eventCd=2629201'

src = io.open('index.html', encoding='utf-8', newline='').read()
before_crlf = src.count('\r\n')
BLOCK = re.compile(r'  \{\r\n    "id": (\d+),.*?\r\n  \},?', re.S)
m = {int(x.group(1)): x for x in BLOCK.finditer(src)}[EID]
e = json.loads(m.group(0).rstrip(',').strip())

ts = e.get('tickets') or []
if any((t.get('url') or '') == URL2 for t in ts):
    print('既に復元済み（2629201 の枠がある）')
    sys.exit(0)

base = dict(ts[0])
base['url'] = URL2
e['tickets'] = ts + [base]


def dump_entry(obj):
    body = json.dumps(obj, ensure_ascii=False, indent=2)
    body = '\n'.join(('  ' + ln) if ln else ln for ln in body.split('\n'))
    return body.replace('\n', '\r\n')


src = src[:m.start()] + dump_entry(e) + (',' if m.group(0).endswith(',') else '') + src[m.end():]

print('=== id%d %s ===' % (EID, e.get('artist', '')))
for t in e['tickets']:
    print('  %s' % t.get('type'))
    print('     → %s' % t.get('url'))
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S).group(2))
chk = [x for x in EV if x['id'] == EID][0]
urls = {t.get('url') for t in chk['tickets']}
print()
print('枠 %d本 / 売り場URL %d本 / 2629201 が入った: %s'
      % (len(chk['tickets']), len(urls), URL2 in urls))
print('総件数 %d' % len(EV))
print('CRLF %d → %d ／ LF単独 %d' % (before_crlf, src.count('\r\n'), src.count('\n') - src.count('\r\n')))

if APPLY:
    io.open('index.html.bak_0817_restore4448', 'w', encoding='utf-8', newline='').write(
        io.open('index.html', encoding='utf-8', newline='').read())
    io.open('index.html', 'w', encoding='utf-8', newline='').write(src)
    print('適用しました（backup: index.html.bak_0817_restore4448）')
else:
    print('（判定のみ。適用するなら --apply）')
