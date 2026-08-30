# -*- coding: utf-8 -*-
"""中村佳穂の -P ページから parse_windows が何を返すかを直接見る（通信して白黒つける）。"""
import sys, importlib.util, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
spec = importlib.util.spec_from_file_location('eh', 'tools/eplus_harvest.py')
eh = importlib.util.module_from_spec(spec)
sys.argv = ['eplus_harvest.py', 'noop']          # main() を走らせない引数
try:
    spec.loader.exec_module(eh)
except SystemExit:
    pass
urls = ["https://eplus.jp/sf/detail/2933580002-P0030039P021001",
        "https://eplus.jp/sf/detail/2933580002-P0030039P021002",
        "https://eplus.jp/sf/detail/2933580002-P0030038P021001"]
for u in urls:
    h = eh.fetch(u)
    ws = eh.parse_windows(h)
    print("==", u)
    for w in ws:
        print("   label=%s | 受付 %s %s 〜 %s %s | status=%s" % (w['label'], w['sd'], w['st'], w['ed'], w['et'], w['status']))
