# -*- coding: utf-8 -*-
"""新設した talkshow へ、既存の「トークが本体」の9件を移す（2026-09-03 ユーザー指示）。

移す＝トーク・講演そのものが公演の本体のもの。
移さない＝トークが添え物のもの（落語会のゲスト対談／上映会＋トーク／舞踊＋トーク／
          お笑い芸人のトークライブは owarai で探す人がいる＝現状維持）。

id6018 だけ extraGenres に seiyuu を残す（声優ファンは声優タブで探す＝両方式。
memory: feedback_genre_both_when_unclear）。
元が engeki のものに extraGenres は付けない＝演劇タブのノイズを減らすのが今回の目的だから。
"""
import re, json, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MOVE = [2648, 2822, 3714, 4017, 5000, 5001, 5052, 5477, 6018]
KEEP_EXTRA = {6018: ['seiyuu']}
PATH = 'index.html'

src = open(PATH, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

hit = 0
for e in events:
    if e['id'] not in MOVE:
        continue
    old = e.get('genre')
    assert old not in ('new', 'talkshow'), 'id%d の genre が %s' % (e['id'], old)
    e['genre'] = 'talkshow'
    if e['id'] in KEEP_EXTRA:
        ex = [g for g in (e.get('extraGenres') or []) if g != 'talkshow']
        for g in KEEP_EXTRA[e['id']]:
            if g not in ex:
                ex.append(g)
        e['extraGenres'] = ex
    hit += 1
    print('  id%-6d %-8s → talkshow%s  %s' % (
        e['id'], old,
        ('+' + '+'.join(e.get('extraGenres') or []) if e.get('extraGenres') else ''),
        (e.get('name') or '')[:42]))

assert hit == len(MOVE), '対象が %d件しか無い' % hit

open('index.html.bak_0903_talkshow', 'w', encoding='utf-8', newline='').write(src)
dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
open(PATH, 'w', encoding='utf-8', newline='').write(
    src[:m.start()] + m.group(1) + dumped + m.group(3) + src[m.end():])
print('=== talkshow へ %d件 ===' % hit)
