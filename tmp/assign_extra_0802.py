"""ユーザー「迷ったら両方で」（2026-08-02）を2件に適用
  3591 MANSAI FANTASY BOX 野村萬斎&オーケストラ・アンサンブル金沢 : classic → +dento
  3598 石見神楽松阪上演会                                        : engeki  → +dento
CRLF保持のためバイナリで読み書き・行単位の置換のみ。
"""
import shutil, json

SRC = r'C:\Users\user\oshinavi\index.html'
BAK = SRC + '.bak_0802_assign_extra'
NL = '\r\n'

TARGETS = {3591: ('classic', ['dento']), 3598: ('engeki', ['dento'])}

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
assert after_crlf == before_crlf + 6, 'CRLF 想定外: %d -> %d' % (before_crlf, after_crlf)

shutil.copyfile(SRC, BAK)
open(SRC, 'wb').write(text.encode('utf-8'))
print('OK backup=%s CRLF %d -> %d' % (BAK, before_crlf, after_crlf))
