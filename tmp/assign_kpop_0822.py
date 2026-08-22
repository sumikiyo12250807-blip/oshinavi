# -*- coding: utf-8 -*-
"""相談に残していた INFINITE(4950) と ONEW(5018) を kpop に振り分ける（2026-08-22 ユーザー決定「じゃK-pop」）。

裏取り＝どちらも韓国のアーティスト。
  4950 = 2026 INFINITE FANMEETING [INFINITE RALLY Ⅴ]（9/22-23 京王アリーナTOKYO）
  5018 = 2026 ONEW CONCERT [ONEW THE LIVE : Q] IN JAPAN（9/22-23 東京体育館・ONEWはSHINeeのメンバー）
ぴあのサブジャンルはどちらも「音楽/海外ROCK・POPS」＝**ぴあにK-POPという区分が無い**だけ。

🚨読み書きはテキストモードで統一する（[[feedback_index_html_crcrlf_trap]]）。
"""
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

TARGET = {4950: 'INFINITE', 5018: 'ONEW'}

path = 'index.html'
h = open(path, encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}

for i in sorted(TARGET):
    e = by[i]
    assert e.get('genre') == 'new', (i, e.get('genre'))
    e['genre'] = 'kpop'
    for k in ('_genre', '_extraGenres', '_piaSub'):
        e.pop(k, None)
    e['verifiedAt'] = '2026-08-22'
    print('id%s %s → kpop' % (i, e['name']))

pool = {e['id'] for e in EVENTS if e.get('genre') == 'new'}
mo = re.search(r'(NEW_ORDER\s*=\s*)(\[[^\]]*\])', h, re.S)
old_order = json.loads(mo.group(2))
new_order = [x for x in old_order if x in pool]

shutil.copyfile(path, path + '.bak_0822_kpop')
body = h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]
# NEW_ORDER は EVENTS より後ろにあるので、書き換えた本文に対してもう一度当てる
mo2 = re.search(r'(NEW_ORDER\s*=\s*)(\[[^\]]*\])', body, re.S)
body = body[:mo2.start(2)] + json.dumps(new_order) + body[mo2.end(2):]
open(path, 'w', encoding='utf-8').write(body)

print('プール %d件 / NEW_ORDER %d→%d' % (len(pool), len(old_order), len(new_order)))
print('適用した（backup: index.html.bak_0822_kpop）')
