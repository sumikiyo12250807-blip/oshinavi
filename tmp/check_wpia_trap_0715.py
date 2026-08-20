#!/usr/bin/env python3
"""削除候補が「w.pia.jpの罠」(券種カード0件だが実は販売中)に嵌ってないか確認。

nobinobi(id2331)で発覚：ぴあが券種を w.pia.jp/t/xxx 形式で出すページは
t.pia.jp の ticketSalesList-2024 構造を持たない → パーサが0券種 → 誤って削除候補化。
判定：券種カード0件 かつ w.pia.jp リンク有り = 🚨罠（削除NG）
"""
import io
import re
import sys
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'tools')
from check_expired import extract_events_array

IDS = [1481, 1532, 2186, 2199, 2221, 2278, 2319]

EVENTS = extract_events_array('index.html')
by_id = {e.get('id'): e for e in EVENTS}


def fetch(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')


for i in IDS:
    e = by_id.get(i)
    url = (e.get('links') or {}).get('pia')
    name = e.get('name')
    try:
        h = fetch(url)
    except Exception as ex:
        print(f'id={i} {name} … 取得失敗 {ex}')
        continue
    cards = h.count('ticketSalesList-2024__item')
    tinfo = h.count('ticketInformation.do')
    wpia = len(re.findall(r'https://w\.pia\.jp/t/[^"]+', h))
    if cards == 0 and wpia > 0:
        verdict = '🚨罠の疑い(削除NG)'
    elif cards == 0 and tinfo == 0:
        verdict = '⚠️券種要素ゼロ(要目視)'
    else:
        verdict = '✅通常ページ(券種カード有り=判定は信用できる)'
    print(f'id={i} {name}')
    print(f'   券種カード{cards} / 購入リンク{tinfo} / w.pia.jpリンク{wpia} → {verdict}')
