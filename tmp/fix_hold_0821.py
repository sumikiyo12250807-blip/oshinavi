# -*- coding: utf-8 -*-
"""3バッチ目の投入前ゲートで止めた3件を、統合先に足す（2026-08-21）。

  4892 米倉利紀 東京12/18-19 → 4890（福岡12/12・熊本12/13）と同じツアー
  4896 桂宮治全国ツアー2026 広島1/31 → 既存 1028 と同じツアー
  4897 桂宮治 全国ツアー2026 新潟11/21 → 同上
（[[feedback_harvest_dedup_check]]＝投入前に既存の同名エントリとの統合を必ず確認する）
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

hold = {e['id']: e for e in json.load(io.open('tmp/hold_merge_0821.json', encoding='utf-8'))}
PLAN = {4890: [4892], 1028: [4896, 4897]}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}

for keep, srcs in PLAN.items():
    a = by[keep]
    for t in a['tickets']:
        t.setdefault('url', (a.get('links') or {}).get('pia'))
    seen = {(t.get('type'), t.get('url')) for t in a['tickets']}
    print('=== id=%d %s 枠%d' % (keep, a.get('name'), len(a['tickets'])))
    for s in srcs:
        b = hold[s]
        for t in b['tickets']:
            t = dict(t)
            t.setdefault('url', (b.get('links') or {}).get('pia'))
            if (t.get('type'), t.get('url')) in seen:
                continue
            seen.add((t.get('type'), t.get('url')))
            a['tickets'].append(t)
            print('    + %s | %s' % (t['type'], t.get('date')))
        if b.get('date') and b['date'] > a.get('date', ''):
            print('    公演日 %s → %s' % (a.get('date'), b['date']))
            a['date'] = b['date']
    a['verifiedAt'] = '2026-08-21'
    print('    → 枠%d' % len(a['tickets']))

# 米倉利紀は東京が加わるので会場表記を更新
e = by[4890]
e['venue'] = '全国ツアー（ROOMS／熊本B.9 V1／東京公演）'
e['prefecture'] = '福岡・熊本・東京'
e['dateLabel'] = '2026年12月12日(土)〜2026年12月19日(土) 福岡・熊本・東京'

shutil.copyfile('index.html', 'index.html.bak_0821_hold')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('\n=== 更新 ===')
