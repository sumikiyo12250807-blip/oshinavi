# -*- coding: utf-8 -*-
"""既存エントリの券種名に残ったぴあ表記の飾り記号(●@等)を掃除。
build_pia_entries.kenshu() を 2026-07-10 に正規化したので、過去分を追随させる。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
MARKS = '　 .・●○◎◆◇■□★☆@＠※〇▼▲'
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
n = 0
for e in EVENTS:
    for t in e.get('tickets', []):
        old = t.get('type') or ''
        new = old.strip(MARKS)
        # 「一般発売@（東京…」のように記号が語中(カッコ直前)にいる形も落とす
        new = re.sub(r'(一般発売|先行|プリセール|プレリザーブ|当日券|当日引換券)[●○◎◆◇■□★☆@＠※〇▼▲]+', r'\1', new)
        # 「◎会員限定◎WILD BLUE先行受付」のように語中に挟まる装飾も落とす
        new = re.sub(r'[●○◎◆◇■□★☆＠▼▲]+', ' ', new).replace('  ', ' ').strip()
        if new != old:
            t['type'] = new
            n += 1
            print(f"  id={e['id']:<5} {old}  ->  {new}")
print(f'=== {n}件 掃除 ===')
if DRY:
    print('(DRY)')
elif n:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0710_badge_marks','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():])
    print('written')
