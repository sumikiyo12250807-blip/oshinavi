# -*- coding: utf-8 -*-
"""API版 sibling_show_urls が NoGoD の5公演・蜈蚣の全公演を拾えるか実測する。"""
import sys, importlib.util
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
spec = importlib.util.spec_from_file_location('eh', 'tools/eplus_harvest.py')
eh = importlib.util.module_from_spec(spec)
argv = sys.argv; sys.argv = ['eplus_harvest.py', '__test__']
try: spec.loader.exec_module(eh)
except SystemExit: pass
sys.argv = argv

for label, u in [("NoGoD", "https://eplus.jp/sf/detail/4588510001-P0030001P021001"),
                 ("蜈蚣",  "https://eplus.jp/sf/detail/4591260001-P0030001P021001")]:
    h = eh.fetch(u)
    urls = eh.sibling_show_urls(h, None, eh.fetch)
    print("== %s == 取れたURL %d本" % (label, len(urls)))
    for x in urls[:20]:
        print("   ", x)
