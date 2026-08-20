# -*- coding: utf-8 -*-
"""相談3件の下書きジャンルだけ直す（ユーザー「お勧めでいい」7/31）。
🚨 genre は "new" のまま・NEW_ORDER も触らない＝プールの件数を動かさない
   （[[feedback_new_pool_ok_before_assign]] 部分返事を全件承認と読まない）。"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

FIX = {
    3521: ('jazz', '音楽/フェスティバル→engekiに倒れていた。屋内ホールのジャズ催し'),
    3523: ('dento', '演歌・邦楽→ローマ字taikoで和楽器判定に当たらずenkaだった。和太鼓'),
    3525: ('dento', '音楽その他→名前fallbackでfes。相模原市民会館＝屋内なので和太鼓のdento'),
}

h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

for e in EVENTS:
    if e['id'] in FIX:
        g, why = FIX[e['id']]
        assert e['genre'] == 'new', 'id=%d が新着でない' % e['id']
        print('id=%d %s' % (e['id'], e['name'][:40]))
        print('   _genre: %s → %s   (%s)' % (e.get('_genre'), g, why))
        e['_genre'] = g

news = [e['id'] for e in EVENTS if e.get('genre') == 'new']
print('\ngenre:new = %d件（変わっていないこと）' % len(news))

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
body = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', body)
print('NEW_ORDER = %d件（触っていないこと）' % len(re.findall(r'\d+', mo.group(2))))

open('index.html.bak_0731pm_draftfix', 'w', encoding='utf-8', newline='').write(h)
open('index.html', 'w', encoding='utf-8', newline='').write(body)
b = open('index.html', 'rb').read()
print('CRLF=%d 単独LF=%d' % (b.count(b'\r\n'), b.count(b'\n') - b.count(b'\r\n')))
