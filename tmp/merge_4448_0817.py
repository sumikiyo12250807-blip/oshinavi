# -*- coding: utf-8 -*-
"""id4476 を id4448 に統合して1エントリにする（ユーザー指示 2026-08-17「1まとめる」）。

同一会場・同一公演日・同一出演者で eventCd だけ2つある案件。1部/2部か重複登録かは
ぴあ・検索・会場サイトのどこにも情報が無く確定できなかったため、**買える枠は両方残す**
（[[feedback_capture_all_deadlines_on_add]]＝買える枠は1つ残らず載せる）。
会場ごとのURLが違うので各ticketに url を付ける（[[feedback_tour_per_ticket_url]]）。
ツアーではなく同一会場なので venue/prefecture/date/dateLabel は触らない
（[[feedback_tour_consolidate]]の「同一会場の複数公演」形）。
あわせてジャンルを chanson（シャンソン）で確定する。

🚨CRLF保持（[[feedback_index_html_crlf_preserve]]）。

  python tmp/merge_4448_0817.py [--apply]
"""
import io, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
KEEP, ABSORB, GENRE = 4448, 4476, 'chanson'

src = io.open('index.html', encoding='utf-8', newline='').read()
before_crlf = src.count('\r\n')
BLOCK = re.compile(r'  \{\r\n    "id": (\d+),.*?\r\n  \},?', re.S)
bl = {int(m.group(1)): m for m in BLOCK.finditer(src)}
A = json.loads(bl[KEEP].group(0).rstrip(',').strip())
B = json.loads(bl[ABSORB].group(0).rstrip(',').strip())

urlA = (A.get('links') or {}).get('pia')
urlB = (B.get('links') or {}).get('pia')
assert urlA and urlB and urlA != urlB, 'ぴあURLが取れない/同一'

# 同一公演の確認（違っていたら統合しない）
for k in ('venue', 'prefecture', 'date'):
    assert A.get(k) == B.get(k), '%s が違う: %r / %r' % (k, A.get(k), B.get(k))

for t in A.get('tickets') or []:
    t.setdefault('url', urlA)
for t in B.get('tickets') or []:
    t.setdefault('url', urlB)

merged = dict(A)
merged['genre'] = GENRE
merged['tickets'] = (A.get('tickets') or []) + (B.get('tickets') or [])
for k in ('_genre', '_extraGenres', '_piaSub'):
    merged.pop(k, None)


def dump_entry(obj):
    body = json.dumps(obj, ensure_ascii=False, indent=2)
    body = '\n'.join(('  ' + ln) if ln else ln for ln in body.split('\n'))
    return body.replace('\n', '\r\n')


src = src[:bl[KEEP].start()] + dump_entry(merged) + \
    (',' if bl[KEEP].group(0).endswith(',') else '') + src[bl[KEEP].end():]

bl = {int(m.group(1)): m for m in BLOCK.finditer(src)}
m = bl[ABSORB]
end = m.end()
if src[end:end + 2] == '\r\n':
    end += 2
src = src[:m.start()] + src[end:]

mo = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])', src)
order = [i for i in json.loads(mo.group(2)) if i not in (KEEP, ABSORB)]
src = src[:mo.start(2)] + json.dumps(order) + src[mo.end(2):]

print('=== id%d ← id%d 統合 ===' % (KEEP, ABSORB))
print('  公演名   %s' % merged.get('artist', ''))
print('  会場/県  %s / %s' % (merged.get('venue', ''), merged.get('prefecture', '')))
print('  公演日   %s' % merged.get('date', ''))
print('  ジャンル %s' % merged.get('genre'))
print('  枠 %d本:' % len(merged['tickets']))
for t in merged['tickets']:
    print('    %s' % t.get('type'))
    print('      → %s' % t.get('url'))

EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S).group(2))
pool = [e['id'] for e in EV if e.get('genre') == 'new']
print()
print('総件数 %d / 新着プール %d件 / NEW_ORDER %d件 / 一致 %s'
      % (len(EV), len(pool), len(order), sorted(pool) == sorted(order)))
print('id%d は残っている: %s ／ id%d は消えた: %s'
      % (KEEP, any(e['id'] == KEEP for e in EV), ABSORB, not any(e['id'] == ABSORB for e in EV)))
print('CRLF %d → %d ／ LF単独 %d' % (before_crlf, src.count('\r\n'), src.count('\n') - src.count('\r\n')))

if APPLY:
    io.open('index.html.bak_0817_merge4448', 'w', encoding='utf-8', newline='').write(
        io.open('index.html', encoding='utf-8', newline='').read())
    io.open('index.html', 'w', encoding='utf-8', newline='').write(src)
    print('適用しました（backup: index.html.bak_0817_merge4448）')
else:
    print('（判定のみ。適用するなら --apply）')
