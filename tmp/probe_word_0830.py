# -*- coding: utf-8 -*-
"""e+ のアーティストページ（/sf/word/xxx）の構造を調べる＝全公演のURLがどう並んでいるか。"""
import sys, importlib.util, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
spec = importlib.util.spec_from_file_location('eh', 'tools/eplus_harvest.py')
eh = importlib.util.module_from_spec(spec)
argv = sys.argv; sys.argv = ['eplus_harvest.py', '__probe__']
try: spec.loader.exec_module(eh)
except SystemExit: pass
sys.argv = argv

h = eh.fetch("https://eplus.jp/sf/word/0000022177")
print("HTMLの長さ:", len(h))
links = re.findall(r'href="(/sf/detail/[^"]+)"', h)
print("公演リンク(detail):", len(links))
for u in dict.fromkeys(links):
    print("  ", u)
# 公演カードの日付・会場
cards = re.findall(r'ticket-item__date[^>]*>(.*?)</', h, re.S)[:10]
print("\n日付らしき断片:", [re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',c)).strip()[:30] for c in cards])
# 公演ページ側に /sf/word/ へのリンクがあるか
h2 = eh.fetch("https://eplus.jp/sf/detail/4588510001-P0030001P021001")
w = re.findall(r'/sf/word/(\d+)', h2)
print("\n公演ページ内の /sf/word/ リンク:", list(dict.fromkeys(w))[:5])
