# -*- coding: utf-8 -*-
"""e+ の詳細ページの受付の窓（section）ごとに、本文（券種名・料金・注意書き）を平文で並べる（読むだけ・2026-09-14）。
窓の見出しが同じ（「先着 受付」が2つ）で、どちらがライブ配信でどちらがアーカイブか見出しだけでは分からない時に使う。
使い方: python tmp/eplus_section_text_0914.py <URL>
"""
import re
import sys

sys.path.insert(0, 'tools')
import eplus_harvest as eh

sys.stdout.reconfigure(encoding='utf-8')
h = eh.fetch(sys.argv[1])
secs = [s for s in re.split(r'(?=<section class="block-ticket">)', h) if s.startswith('<section class="block-ticket">')]
for n, sec in enumerate(secs, 1):
    body = sec.split('</section>', 1)[0]
    print('--- 窓%d' % n)
    print(eh._flat(body)[:900])
