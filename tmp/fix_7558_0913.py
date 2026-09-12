# -*- coding: utf-8 -*-
"""id7558 の「一般発売」枠だけに予定枚数終了の印を付ける（2026-09-13 朝）。

なぜ道具を使わないか＝`mark_soldout.py` はエントリ単位で判定するので、
同じエントリに買える枠（この子は「抽選受付中 〜10/20 11:00」）が1つでもあると alive で打ち切り、
一部だけ完売した枠に印を付けられない（memory feedback_heal_flattens_ticket_types の2026-09-01項）。

根拠＝ぴあ b2670145 の生HTML。一般発売＝[予定枚数終了]／先行＝[抽選受付中 〜2026/10/20 11:00]。
（tmp/statustext_bundle_0913.txt。別エージェントも独立に同じ結論を出している）
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = '2026-09-13'
APPLY = '--apply' in sys.argv
path = 'index.html'
# 🚨 newline を指定しない＝読みで CRLF を改行1文字に畳み、書きで CRLF に戻す。
#    newline='' で読んで書くと改行が LF のまま出て index.html が丸ごと LF 化する
#    （2026-09-13 に一度やってしまった＝memory feedback_index_html_crlf_preserve）。
src = io.open(path, encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
ev = json.loads(m.group(2))

hit = 0
for e in ev:
    if e['id'] != 7558:
        continue
    for t in e.get('tickets') or []:
        if (t.get('type') or '').startswith('一般発売'):
            t['soldout'] = True
            t['soldoutSince'] = TODAY
            hit += 1
            print('印を付ける:', t['type'])

if hit != 1:
    print('⚠️ 対象が %d枠＝中止' % hit)
    sys.exit(1)
if not APPLY:
    print('（--apply で適用）')
    sys.exit(0)

io.open('index.html.bak_0913_fix7558', 'w', encoding='utf-8').write(src)
out = src[:m.start()] + m.group(1) + json.dumps(ev, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():]
io.open(path, 'w', encoding='utf-8').write(out)
print('✅ 適用したわ（backup: index.html.bak_0913_fix7558）')
