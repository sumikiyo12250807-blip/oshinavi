"""新着プール46件の振り分け（ユーザー「振り分けお願い」2026-08-02）
方針: _genre をそのまま genre へ（project_vendor_genre_autoassign）。
人が決めたのは _piaSub が「その他」の2件だけ:
  3578 Electone Concert … 名前fallbackの fes は誤り（屋内・3名の器楽演奏会）→ classic + kids(親子ペア券あり)
  3616 0歳からのクラシック … classic + kids（親子券・0歳から）
CRLF保持のためバイナリで読み書きし、行単位の文字列置換のみ行う。
"""
import re, sys, shutil, json

sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from check_expired import extract_events_array

SRC = r'C:\Users\user\oshinavi\index.html'
BAK = SRC + '.bak_0802_assign'

# 人が決めた分だけ上書き（他は _genre をそのまま）
OVERRIDE = {
    3578: ('classic', ['kids']),
    3616: ('classic', ['kids']),
}

events = extract_events_array(SRC)
pool = [e for e in events if e.get('genre') == 'new']
assert len(pool) == 46, 'プール件数が想定外: %d' % len(pool)

text = open(SRC, 'rb').read().decode('utf-8')
before_crlf = text.count('\r\n')
NL = '\r\n'

applied = []
for e in pool:
    eid = e['id']
    g, extra = OVERRIDE.get(eid, (e.get('_genre'), list(e.get('_extraGenres') or [])))
    assert g, 'id=%d: _genre が空' % eid

    key = '"id": %d,' % eid
    i = text.index(key)
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

    old = '    "genre": "new",' + NL
    old += '    "_genre": %s,' % json.dumps(e.get('_genre'), ensure_ascii=False) + NL
    old += '    "_extraGenres": %s,' % json.dumps(e.get('_extraGenres') or [], ensure_ascii=False) + NL
    old += '    "_piaSub": %s,' % json.dumps(e.get('_piaSub'), ensure_ascii=False) + NL
    assert b.count(old) == 1, 'id=%d: 下書き4行が一致しない' % eid

    new = '    "genre": "%s",' % g + NL
    if extra:
        new += '    "extraGenres": [' + NL
        new += (',' + NL).join('      %s' % json.dumps(x, ensure_ascii=False) for x in extra) + NL
        new += '    ],' + NL

    text = text[:st] + b.replace(old, new) + text[en:]
    applied.append((eid, g, extra))

# NEW_ORDER を空に
m = re.search(r'const NEW_ORDER = \[[^\]]*\];', text)
assert m, 'NEW_ORDER が見つからない'
text = text[:m.start()] + 'const NEW_ORDER = [];' + text[m.end():]

# 下書きキーが残っていないこと
for k in ('"_genre"', '"_extraGenres"', '"_piaSub"'):
    assert k not in text, '%s が残っている' % k

after_crlf = text.count('\r\n')
shutil.copyfile(SRC, BAK)
open(SRC, 'wb').write(text.encode('utf-8'))

rep = ['振り分け %d件 (backup=%s)' % (len(applied), BAK),
       'CRLF %d -> %d' % (before_crlf, after_crlf)]
for eid, g, extra in applied:
    rep.append('id=%d -> %s%s' % (eid, g, ('+' + '/'.join(extra)) if extra else ''))
open(r'C:\Users\user\oshinavi\tmp\assign_0802.txt', 'w', encoding='utf-8').write('\n'.join(rep))
print('OK applied=%d CRLF %d -> %d' % (len(applied), before_crlf, after_crlf))
