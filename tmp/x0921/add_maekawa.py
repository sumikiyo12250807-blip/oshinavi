# -*- coding: utf-8 -*-
"""id17274 前川清の配信に、ぴあの 9/24 10:00 一般発売の枠を足し算で入れる（古い10/1の枠は残す＝安全弁の決まり）。
改行コードはそのまま（heal_stale_deadlines と同じ読み書き）。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
h = open(P, encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
ev = json.loads(m.group(2))
NEW = {"type": "一般発売（全国 10/17〜10/21公演）9/24 10:00発売", "date": "2026-09-24", "startDate": "2026-09-24"}
n = 0
for e in ev:
    if e['id'] == 17274:
        if any(t.get('startDate') == '2026-09-24' for t in e['tickets']):
            print('もう入っている'); sys.exit()
        e['tickets'].insert(0, NEW)
        n += 1
assert n == 1
# 元の書式（1行1エントリ）に合わせるため、該当エントリの行だけ差し替える


open('index.html.bak_0921_maekawa', 'w', encoding='utf-8').write(h)
open(P, 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + json.dumps(ev, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('足した: id17274 9/24 10:00 一般発売')
