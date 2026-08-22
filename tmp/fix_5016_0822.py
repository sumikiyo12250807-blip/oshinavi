# -*- coding: utf-8 -*-
"""5016 TJHiroshimaチケット企画＝同じ文言のバッジが4枚×2組並んでいた（2026-08-22）。

実体は**ゴルフ場4か所の別企画**（久井カントリークラブ／呉カントリークラブ／
広島西カントリー倶楽部／鷹の巣ゴルフクラブ）で、ぴあのパーサーが券種名を落として潰していた
（[[feedback_pia_parser_flattens_slots]]＝本当の枠数はリンク先 lotRlsCd のユニーク数）。
各枠の `title` にちゃんと企画名が入っていたので、そこから取ってバッジ文言に入れ、
枠ごとに飛び先URLを持たせる（[[feedback_dedup_badges_keeps_urls]]＝畳むと売り場への導線が消える）。

⚠️公演日は触らない＝`perf_end` が 2027-03-24 / 2027-04-24 まで伸びているシーズン券の形で、
   登録の `date=2027-04-24` もバッジの「9/25〜R9年 4/24公演」も正しい。
"""
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

rows = json.load(open('tmp/p5016.json', encoding='utf-8'))
buy = [r for r in rows if r['state'] in ('受付中', '発売前')]
assert len(buy) == 8, len(buy)

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
e = {x['id']: x for x in EVENTS}[5016]
old = {t['type'] for t in e['tickets']}
assert len(old) == 2 and len(e['tickets']) == 8, '前提が変わっている'

tickets = []
for r in buy:
    # title 例: TJHiroshima8月号久井カントリークラブ企画〔広島〕
    mm = re.search(r'TJHiroshima(\d+月号)(.+?)企画', r['title'])
    assert mm, r['title']
    label = '%s %s' % (mm.group(1), mm.group(2))
    if r['state'] == '受付中':
        t = {'type': '先行【%s】（広島 8/25〜R9年 3/24公演）〜8/22 12:00' % label,
             'date': '2026-08-22', 'url': r['url']}
    else:
        t = {'type': '先行【%s】（広島 9/25〜R9年 4/24公演）8/22 11:00発売' % label,
             'date': '2026-09-20', 'startDate': '2026-08-22', 'url': r['url']}
    tickets.append(t)

assert len({t['type'] for t in tickets}) == 8, '文言の重複が残っている'
assert len({t['url'] for t in tickets}) == 8, 'URLの重複が残っている'

e['tickets'] = tickets
e['verifiedAt'] = '2026-08-22'
for t in tickets:
    print(' -', t['type'])

shutil.copyfile('index.html', 'index.html.bak_0822_5016')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('適用した（公演日・dateLabel は触っていない）')
