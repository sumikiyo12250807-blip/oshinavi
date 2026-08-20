# -*- coding: utf-8 -*-
"""新着(id2765-2814)のぴあURL検証・改良版。
判定はis_error_page＋本文の「見つかりませんでした」等でDEADのみ厳密検出。
タイトルは参考表示（照合の誤検出を出さない）。"""
import re, sys, json, importlib.util, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

_spec = importlib.util.spec_from_file_location('bpe', 'tools/build_pia_entries.py')
bpe = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(bpe)

h = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS\s*=\s*(\[.*?\n\];)', h, re.S)
data = json.loads(m.group(1)[:-1])
targets = [e for e in data if e.get('genre') == 'new']

def title_of(html):
    mm = re.search(r'<title>([^<]*)</title>', html or '')
    return (mm.group(1).strip() if mm else '')

print(f"検証対象 {len(targets)}件\n")
dead, ok = [], []
for e in targets:
    pia = (e.get('links') or {}).get('pia') or ''
    if not pia:
        print(f"  (piaリンク無) id{e['id']} {e['name'][:20]}"); continue
    try:
        html = bpe.fetch(pia)
    except Exception as ex:
        dead.append((e['id'], e['name'], pia, f'FETCH_ERR'));
        print(f"🚨DEAD id{e['id']} {e['name'][:24]} FETCH_ERR"); continue
    notfound = ('見つかりませんでした' in html) or ('ご指定の公演' in html) or ('指定された公演' in html)
    if bpe.is_error_page(html) or notfound:
        dead.append((e['id'], e['name'], pia, 'error'));
        print(f"🚨DEAD id{e['id']} {e['name'][:24]} | {pia}"); continue
    ok.append(e['id'])

print(f"\n=== 集計: OK {len(ok)} / 🚨DEAD {len(dead)} ===")
if dead:
    print("[DEAD一覧]")
    for d in dead: print(f"  id{d[0]} {d[1]} | {d[2]}")
else:
    print("全URL生存・有効イベントを指している ✅")
