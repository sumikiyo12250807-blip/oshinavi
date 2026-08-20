# -*- coding: utf-8 -*-
"""ユーザー回答の適用（7/31昼）。
 ③ 3550 親子のためのプラザdeこども寄席 → _extraGenres に kids を足す（下書きのみ・genreはnewのまま）
 ④ 3549 東京バレエ団「くるみ割り人形」→ ユーザー提供の Amazon リンク（チャイコフスキー CD）に差し替え
    [[reference_amazon_affiliate]] ユーザー提供リンクは自動生成より優先（curated優先）
"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

AMZ = 'https://amzn.to/45x5l95'   # k=チャイコフスキー CD / tag=oshinavi0a-22（ユーザー提供）

h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

e50 = next(x for x in EVENTS if x['id'] == 3550)
assert e50['genre'] == 'new'
e50['_extraGenres'] = ['kids']
print('3550 %s → _genre=%s _extraGenres=%s' % (e50['name'][:30], e50.get('_genre'), e50['_extraGenres']))

e49 = next(x for x in EVENTS if x['id'] == 3549)
print('3549 %s' % e49['name'][:40])
print('   amazon 旧: %s' % (e49['links'].get('amazon') or '')[:70])
e49['links']['amazon'] = AMZ
print('   amazon 新: %s' % AMZ)

news = [x['id'] for x in EVENTS if x.get('genre') == 'new']
print('genre:new = %d件（変わっていないこと）' % len(news))

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
body = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
open('index.html.bak_0731pm_answers', 'wb').write(h.encode('utf-8'))
open('index.html', 'wb').write(body.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8'))
b = open('index.html', 'rb').read()
print('CRLF=%d 単独LF=%d' % (b.count(b'\r\n'), b.count(b'\n') - b.count(b'\r\n')))
