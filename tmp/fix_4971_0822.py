# -*- coding: utf-8 -*-
"""4971 映画『ホーム スイート ホーム』舞台挨拶＝別会場の枠が同じ文言に潰れていた（2026-08-22）。

🚨これは [[feedback_pia_parser_flattens_slots]] の型で、放っておくと
   [[feedback_dedup_badges_keeps_urls]] の事故になる＝`dedup_badges.py` を流した瞬間に
   「9/5 東京」の2枠（イオンシネマ板橋／kino cinema 新宿）が畳まれて**別の売り場への導線が2本消える**。
   しかも tickets[].url が全部 null なので、url が違えば残すという保険も効かない。

直し方＝ぴあの実ページ（bundle b2669792）から10枠をゼロから再導出し、
   ①バッジ文言に**会場名**を入れて画面で見分けられるようにする（[[feedback_same_day_show_time_badge]]の考え方）
   ②**枠ごとに飛び先URL**を持たせる（会場別に10通り）
   ③name を実ページどおり「公開記念舞台挨拶」にする
"""
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

rows = json.load(open('tmp/p4971.json', encoding='utf-8'))
buy = [r for r in rows if r['state'] in ('受付中', '発売前')]
assert len(buy) == 10, len(buy)

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
e = {x['id']: x for x in EVENTS}[4971]


def pref(p):
    return re.sub(r'(都|府|県)$', '', p or '')


def md(d):
    y, mo, dd = d.split('-')
    return '%d/%d' % (int(mo), int(dd))


tickets = []
for r in buy:
    ven = r['venue'].replace('ｋｉｎｏ ｃｉｎｅｍａ', 'kino cinema')
    if r['state'] == '受付中':
        t = {'type': '先行【%s】（%s %s公演）〜8/23 23:59' % (ven, pref(r['pref']), md(r['perfdate'])),
             'date': '2026-08-23', 'url': r['url']}
    else:
        t = {'type': '一般発売【%s】（%s %s公演）8/25 10:00発売' % (ven, pref(r['pref']), md(r['perfdate'])),
             'date': '2026-08-25', 'startDate': '2026-08-25', 'url': r['url']}
    tickets.append(t)

# 文言が全部ユニークになったことを機械で確かめる（潰れが残っていたら止める）
assert len({t['type'] for t in tickets}) == 10, '文言の重複が残っている'
assert len({t['url'] for t in tickets}) == 10, 'URLの重複が残っている'

e['tickets'] = tickets
e['name'] = '映画『ホーム スイート ホーム』公開記念舞台挨拶'
e['artist'] = e['name']
e['verifiedAt'] = '2026-08-22'

for t in tickets:
    print(' -', t['type'])
print('枠 %d（文言・URLとも全部ユニーク）' % len(tickets))

shutil.copyfile('index.html', 'index.html.bak_0822_4971')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('適用した')
