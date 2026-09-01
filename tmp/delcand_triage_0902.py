# -*- coding: utf-8 -*-
"""ヒールが出した削除候補を、消す前に分類する（通信なし・DELETE_GATE.md の3章に対応）。

出す分類:
  A ぴあ以外にも売り場がある      → ぴあだけ見て消してはいけない
  B 売り切れ/販売終了マーク済み    → 消さない（表示し続ける）
  C 公演が31日より先で枠0         → 一般発売がまだ出ていない疑い（消さずヒール待ち）
  D 公演が近い（30日以内）で枠0    → 前売り終了の可能性・要確認
  E 公演が過ぎている              → 削除ルート
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
TODAY = '2026-09-02'
LOG = 'tmp/heal_apply_0902.log'

txt = open(LOG, encoding='utf-8').read()
sec = txt.split('買える枠ゼロ = 削除候補')[1] if '買える枠ゼロ = 削除候補' in txt else ''
ids = [int(x) for x in re.findall(r'^  id=(\d+)', sec, re.M)]
print(f'削除候補 {len(ids)}件')

h = open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
by = {e['id']: e for e in EV}

import datetime
td = datetime.date.fromisoformat(TODAY)
buckets = {k: [] for k in 'ABCDE'}
for i in ids:
    e = by.get(i)
    if not e:
        continue
    urls = [(t.get('url') or '') for t in (e.get('tickets') or [])]
    urls += [((e.get('links') or {}).get(k) or '') for k in ('pia', 'rakuten', 'eplus', 'ltike', 'official')]
    nonpia = sorted({u.split('/')[2] for u in urls if u and 'pia.jp' not in u})
    marked = any(t.get('soldout') or t.get('saleEnded') for t in (e.get('tickets') or []))
    d = e.get('date') or ''
    try:
        days = (datetime.date.fromisoformat(d) - td).days
    except Exception:
        days = None
    if nonpia:
        k = 'A'
    elif marked:
        k = 'B'
    elif days is None:
        k = 'D'
    elif days < 0:
        k = 'E'
    elif days > 30:
        k = 'C'
    else:
        k = 'D'
    buckets[k].append((i, e.get('artist', '')[:34], d, days, ','.join(nonpia)[:50]))

names = {'A': 'ぴあ以外にも売り場がある（ぴあだけで消してはダメ）',
         'B': '売り切れ/販売終了マーク済み（消さない）',
         'C': '公演が31日より先で枠0（一般発売がまだ出ていない疑い）',
         'D': '公演が30日以内で枠0（前売り終了の可能性・要確認）',
         'E': '公演が過ぎている（削除ルート）'}
for k in 'EDCBA':
    print(f'\n=== {k} {names[k]} … {len(buckets[k])}件')
    for i, n, d, days, np in buckets[k]:
        print(f'  id={i:<5} 公演{d} (あと{days}日) {n}  {np}')
