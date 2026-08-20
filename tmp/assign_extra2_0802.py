"""ユーザーOK（2026-08-02）: 水瀬いのり id=3582 を jpop + seiyuu に"""
import shutil, json

SRC = r'C:\Users\user\oshinavi\index.html'
BAK = SRC + '.bak_0802_assign_extra2'
NL = '\r\n'
TARGETS = {3582: ('jpop', ['seiyuu'])}

text = open(SRC, 'rb').read().decode('utf-8')
before_crlf = text.count('\r\n')

for eid, (g, extra) in TARGETS.items():
    i = text.index('"id": %d,' % eid)
    st = text.rindex('{', 0, i)
    depth = 0
    for j in range(st, len(text)):
        if text[j] == '{':
            depth += 1
        elif text[j] == '}':
            depth -= 1
            if depth == 0:
                en = j + 1
                break
    b = text[st:en]
    assert '"extraGenres"' not in b, 'id=%d: 既に extraGenres がある' % eid
    old = '    "genre": "%s",' % g + NL
    assert b.count(old) == 1, 'id=%d: genre行が一致しない' % eid
    new = old + '    "extraGenres": [' + NL
    new += (',' + NL).join('      %s' % json.dumps(x, ensure_ascii=False) for x in extra) + NL
    new += '    ],' + NL
    text = text[:st] + b.replace(old, new) + text[en:]

after_crlf = text.count('\r\n')
assert after_crlf == before_crlf + 3, 'CRLF 想定外: %d -> %d' % (before_crlf, after_crlf)
shutil.copyfile(SRC, BAK)
open(SRC, 'wb').write(text.encode('utf-8'))
print('OK backup=%s CRLF %d -> %d' % (BAK, before_crlf, after_crlf))
