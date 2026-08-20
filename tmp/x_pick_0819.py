# -*- coding: utf-8 -*-
"""明日(2026-08-19)に発売が始まる枠を機械抽出する。X投稿の候補出し用。
判定＝ticket.startDate == 対象日（発売開始が明示されている枠だけ）。
[[feedback_sale_start_vs_deadline]]＝date(締切)を発売開始と読み違えないこと。
"""
import io, json, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

TARGET = sys.argv[1] if len(sys.argv) > 1 else '2026-08-19'

raw = io.open('index.html', 'r', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n', raw, re.S).group(1))

rows = []
for e in EVENTS:
    hits = [t for t in (e.get('tickets') or [])
            if t.get('startDate') == TARGET and not t.get('soldout')]
    if hits:
        rows.append((e, hits))

print('=== %s に発売開始の枠を持つエントリ: %d件 ===' % (TARGET, len(rows)))
print()
for e, hits in rows:
    links = e.get('links') or {}
    print('id%-5s %-30s %s' % (e['id'], (e.get('artist') or '')[:28], e.get('genre')))
    print('       会場=%s / 公演日=%s / %s' % ((e.get('venue') or '')[:38], e.get('date'), e.get('prefecture')))
    for t in hits:
        print('       枠: %s' % t.get('type'))
    print('       %s' % (links.get('pia') or links.get('eplus') or links.get('rakuten') or ''))
    print()

g = collections.Counter(e.get('genre') for e, _ in rows)
print('ジャンル内訳: ' + ' / '.join('%s=%d' % kv for kv in g.most_common()))
