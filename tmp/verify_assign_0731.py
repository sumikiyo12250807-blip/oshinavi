# -*- coding: utf-8 -*-
"""振り分け＋統合後の機械チェック（CRLF維持 / genre:new / NEW_ORDER / 下書き残骸 / 2544の中身）。"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

def crlf_stat(path):
    b = open(path, 'rb').read()
    crlf = b.count(b'\r\n')
    lf = b.count(b'\n')
    return crlf, lf - crlf, len(b)

for p in ('index.html.bak_0731_assign', 'index.html.bak_0731_merge_ultra', 'index.html'):
    crlf, lone_lf, size = crlf_stat(p)
    print('%-34s CRLF=%d  単独LF=%d  bytes=%d' % (p, crlf, lone_lf, size))

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))
print('総エントリ数 =', len(EVENTS))

news = [e['id'] for e in EVENTS if e.get('genre') == 'new']
print('genre:new =', len(news), news)
mo = re.search(r'(const\s+NEW_ORDER\s*=\s*)(\[[^\]]*\])', h)
print('NEW_ORDER =', mo.group(2))
print('id3515 の残存 =', any(e['id'] == 3515 for e in EVENTS))

resid = [e['id'] for e in EVENTS if any(k in e for k in ('_genre', '_extraGenres', '_piaSub', '_srcgenre'))]
print('下書きフィールド残り =', resid)

for eid in (2544, 3510):
    e = next(x for x in EVENTS if x['id'] == eid)
    print('--- id=%d %s' % (eid, e['name'][:40]))
    print('    genre=%s extraGenres=%s links=%s' % (
        e['genre'], e.get('extraGenres'), {k: bool(v) for k, v in e['links'].items() if v}))
    for t in e['tickets']:
        print('      %-56s date=%s start=%s url=%s' % (
            t['type'], t['date'], t.get('startDate', '-'),
            'ぴあ' if 't.pia.jp' in (t.get('url') or '') else ('楽天' if t.get('url') else 'なし')))

# バッジ形式チェック（公演日が完全M/D形で（…公演）内にあるか）
bad = [t['type'] for t in next(x for x in EVENTS if x['id'] == 2544)['tickets']
       if not re.search(r'（[^）]*\d{1,2}/\d{1,2}[^）]*公演）', t['type'])]
print('2544 バッジ形式NG =', bad)
