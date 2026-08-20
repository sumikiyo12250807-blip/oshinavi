# -*- coding: utf-8 -*-
"""ツアーのまとめページ(eventBundleCd)から、ぶら下がっている各公演の eventCd を洗い出す。

背景（2026-08-18 ユーザー発見）＝ハンブレッダーズのまとめページには東京10/2の一般発売しか
出ないのに、名古屋10/30は別ページ(eventCd=2628145)に「9/6発売」で立っていた。
まとめページだけ見ていると【発売前の公演が丸ごと見えない】。
"""
import re, sys
sys.path.insert(0, 'tools')
import build_pia_entries as bpe
sys.stdout.reconfigure(encoding='utf-8')

url = sys.argv[1]
h = bpe.fetch(url)
print('len(html)=%d' % len(h))

cds = []
for m in re.finditer(r'event\.do\?eventCd=(\d+)', h):
    if m.group(1) not in cds:
        cds.append(m.group(1))
print('個別公演の eventCd: %d件' % len(cds))
print(','.join(cds))

for m in re.finditer(r'ticketInformation\.do\?([^"&]*(?:&[^"]*)?)', h):
    pass

# 参考: まとめページ自身の券種カード
print()
print('--- まとめページの券種カード ---')
for r in bpe.parse_cards(h):
    print('%-8s %-14s %-30s %s' % (r['state'], r['perfdate'], (r['title'] or '')[:28],
                                   bpe.slot_code(r.get('url'))))
