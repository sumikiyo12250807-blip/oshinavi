# -*- coding: utf-8 -*-
"""楽天の枠を持つ全エントリを、公演ごとの売り状態APIで調べて「予定枚数終了」を付ける。

  python tmp/rakuten_soldout_sweep_0910.py          … 調べるだけ
  python tmp/rakuten_soldout_sweep_0910.py --apply  … index.html に印を付ける

🚨2026-09-10 ユーザー発見「木下グループが売り切れ出てる」。
   楽天の売り状態は生HTMLに無く、購入ボタンのAJAXにしか出ない（tools/rakuten_perf_status.py）。
   だから今まで**売り切れた楽天の枠を「買える」として出し続けていた**。

判定の作法（[[feedback_saleended_vs_soldout]]）:
 ・枠が名乗っている公演日（バッジの「（県 M/D公演）」）に当たる**その公演のカード**だけを見る
 ・その公演のカードが**全部 soldout** の時だけ印を付ける（1枚でも買えるなら触らない）
 ・楽天が「予定枚数終了」と明記しているので `soldout`（`saleEnded` は付けない）
 ・売り切れは**消さない**（[[feedback_soldout_keep_visible]]）
 ・逆向きも見る＝買えるようになっていたら印を外す
"""
import datetime
import json
import re
import sys
import urllib.parse

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

TODAY = datetime.date.today().isoformat()
APPLY = '--apply' in sys.argv


def raw_url(u):
    m = re.search(r'murl=([^&]+)', u or '')
    return urllib.parse.unquote(m.group(1)) if m else (u or '')


def md(iso_s):
    return '%d/%d' % (int(iso_s[5:7]), int(iso_s[8:10]))


src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

targets = []
for e in events:
    slots = [t for t in (e.get('tickets') or []) if 'rakuten' in raw_url(t.get('url'))]
    if not slots:
        continue
    urls = []
    for t in slots:
        u = raw_url(t['url'])
        if u not in urls:
            urls.append(u)
    lr = raw_url((e.get('links') or {}).get('rakuten'))
    if lr and lr not in urls:
        urls.append(lr)
    targets.append((e, slots, urls))

print('楽天の枠を持つエントリ %d件' % len(targets))

cache = {}
marked, unmarked, skipped, lines = 0, 0, [], []
for e, slots, urls in targets:
    rows = []
    bad = None
    for u in urls:
        if u not in cache:
            try:
                cache[u] = P.perf_status(u)
            except Exception as ex:
                cache[u] = {'ok': False, 'why': repr(ex)[:80], 'rows': []}
        r = cache[u]
        if not r.get('ok'):
            bad = r.get('why')
            continue
        rows += r['rows']
    if not rows:
        skipped.append((e['id'], e['name'][:40], bad or '公演カードが取れない'))
        continue

    by_md = {}
    for c in rows:
        by_md.setdefault(md(c['date']), []).append(c)

    for t in slots:
        bm = re.search(r'（[^（）]*?((?:R\d+年\s*)?\d{1,2}/\d{1,2}(?:〜(?:R\d+年\s*)?\d{1,2}/\d{1,2})?)'
                       r'(?:\s+\d{1,2}:\d{2})?公演）', t.get('type') or '')
        if not bm:
            continue
        days = [re.sub(r'^R\d+年\s*', '', x.strip()) for x in bm.group(1).split('〜')]
        cs = []
        for d in days:
            cs += by_md.get(d, [])
        if not cs:
            continue                      # ページに残っていない公演＝判定しない
        allsold = all(c['status'] == 'soldout' for c in cs)
        anybuy = any(c['status'] == 'buyable' for c in cs)
        if allsold and not t.get('soldout'):
            t['soldout'] = True
            t['soldoutSince'] = TODAY
            t.pop('saleEnded', None)
            t.pop('saleEndedSince', None)
            marked += 1
            lines.append('  🔴 id=%-5s %-44s → 予定枚数終了' % (e['id'], t['type'][:44]))
        elif anybuy and t.get('soldout'):
            t.pop('soldout', None)
            t.pop('soldoutSince', None)
            unmarked += 1
            lines.append('  🟢 id=%-5s %-44s → 買えるので印を外す' % (e['id'], t['type'][:44]))

print('\n印を付けた %d枠 / 外した %d枠 / 調べられなかった %d件' % (marked, unmarked, len(skipped)))
for l in lines:
    print(l)
if skipped:
    print('\n⏭️ 調べられなかった（ページ形式が違う＝要目視）')
    for i, n, why in skipped:
        print('  id=%-5s %-40s %s' % (i, n, why))

if not APPLY:
    print('\n(--apply で書き込み)')
    sys.exit(0)

arr = json.dumps(events, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
print('\n書き込み完了')
