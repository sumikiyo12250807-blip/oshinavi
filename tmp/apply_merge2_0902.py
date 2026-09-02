# -*- coding: utf-8 -*-
"""統合4組を既存エントリへ当てる。「追加と補完だけ・置換で枠を殺さない」。

  695 TOMOVSKY ← 新6290 ／ 4223 レオてつ ← 新6332
  2111 エリザベート弦楽アンサンブル ← 新6343 ／ 3406 反田恭平 ← 新6352

新候補は投入しない（欠番のまま）。venue/dateLabel/date はツアーが伸びるので再ビルド結果に更新。

  python tmp/apply_merge2_0902.py [--apply]
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
KEEPS = [695, 4223, 2111, 3406]

built = {e['id']: e for e in json.load(open('tmp/merge2_built_0902.json', encoding='utf-8'))}
src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
EV = json.loads(m.group(2))
by = {e['id']: e for e in EV}


def base_type(ty):
    ty = re.sub(r'〜\s*\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*$', '', ty or '')
    ty = re.sub(r'\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*発売\s*$', '', ty)
    return ty.strip()


ng = 0
for k in KEEPS:
    b, e = built[k], by[k]
    before = list(e.get('tickets') or [])
    newk = {base_type(t.get('type')) for t in b['tickets']}
    keepers = [t for t in before if base_type(t.get('type')) not in newk]
    merged = list(b['tickets']) + keepers
    print(f'=== id{k} {e.get("artist","")[:32]}')
    print(f'   枠: 既存{len(before)} → 再ビルド{len(b["tickets"])} + 据置{len(keepers)} = {len(merged)}')
    for t in keepers:
        print(f'   据置: {t.get("type")[:56]}')
    e['tickets'] = merged
    for f in ('venue', 'dateLabel', 'date', 'prefecture'):
        if b.get(f) and b[f] != e.get(f):
            print(f'   {f}: {str(e.get(f))[:46]!r} → {str(b[f])[:46]!r}')
            e[f] = b[f]
if not APPLY:
    print('\n（--apply を付けると書き込む）')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\r\n', '\n').replace('\n', nl)
open('index.html.bak_0902_merge2', 'w', encoding='utf-8', newline='').write(src)
open('index.html', 'w', encoding='utf-8', newline='').write(
    src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
print('\nindex.html を更新（backup: index.html.bak_0902_merge2）')
