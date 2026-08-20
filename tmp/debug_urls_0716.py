# -*- coding: utf-8 -*-
import re, sys, importlib.util
sys.stdout.reconfigure(encoding='utf-8')
_spec = importlib.util.spec_from_file_location('bpe', 'tools/build_pia_entries.py')
bpe = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(bpe)

urls = {
 2780:'https://t.pia.jp/pia/event/event.do?eventCd=2628635',
 2782:'https://t.pia.jp/pia/event/event.do?eventCd=2628285',
 2783:'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669865',
 2784:'https://t.pia.jp/pia/event/event.do?eventCd=2625179',
 2793:'https://t.pia.jp/pia/event/event.do?eventCd=2623768',
 2796:'https://t.pia.jp/pia/event/event.do?eventCd=2626306',
 2798:'https://t.pia.jp/pia/event/event.do?eventCd=2617391',
 2801:'https://t.pia.jp/pia/event/event.do?eventCd=2627902',
 2805:'https://t.pia.jp/pia/event/event.do?eventCd=2626268',
}
for id,u in urls.items():
    try:
        html = bpe.fetch(u)
    except Exception as ex:
        print(f"id{id} FETCH_ERR {ex}"); continue
    err = bpe.is_error_page(html)
    notfound = ('見つかりませんでした' in html) or ('ご指定の公演' in html) or ('指定された公演' in html)
    mt = re.search(r'<title>([^<]*)</title>', html)
    title = mt.group(1).strip() if mt else '(title無)'
    try:
        cards = bpe.parse_cards(html)
        nc = len(cards)
    except Exception as ex:
        nc = f'ERR({ex})'
    print(f"id{id} err={err} notfound={notfound} cards={nc}\n   title={title}\n   {u}")
