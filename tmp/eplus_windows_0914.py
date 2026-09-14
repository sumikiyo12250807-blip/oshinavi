# -*- coding: utf-8 -*-
"""e+ の詳細ページ（-P URL）の受付期間の窓を、終わった窓も含めて全部並べる（読むだけ・2026-09-14）。
公演名・公演日（ドロップダウン）・窓の見出し・受付期間・状態の文言を出す。1ページずつ1秒あける。
使い方: python tmp/eplus_windows_0914.py <URL> [<URL> ...]
"""
import re
import sys
import time

sys.path.insert(0, 'tools')
sys.path.insert(0, 'tmp')
import eplus_harvest as eh

sys.stdout.reconfigure(encoding='utf-8')
for u in sys.argv[1:]:
    print('=== %s' % u)
    try:
        h = eh.fetch(u)
    except Exception as ex:
        print('  読めない: %s' % ex)
        continue
    t = re.search(r'<title>(.*?)</title>', h, re.S)
    print('  題: %s' % eh._flat(t.group(1))[:100] if t else '  題: -')
    for o in re.findall(r'<option value="\d{8}[^"]*">([^<]+)</option>', h):
        print('  公演: %s' % eh._flat(o))
    secs = [s for s in re.split(r'(?=<section class="block-ticket">)', h) if s.startswith('<section class="block-ticket">')]
    for sec in secs:
        body = sec.split('</section>', 1)[0]
        span = re.search(r'<span class="ticket-status__item[^"]*">([^<]+)</span>', body)
        hm = re.search(r'block-ticket__header[^>]*>(.*?)</header>', body, re.S)
        print('  窓: %s ｜状態: %s' % (eh._flat(hm.group(1) if hm else '')[:140], (span.group(1).strip() if span else '-')))
    time.sleep(1.0)
