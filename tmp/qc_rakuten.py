# -*- coding: utf-8 -*-
"""楽天エントリの投入前QC＝表示に出る値の粗チェック。"""
import json, re, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

rows = json.load(open('tmp/built_rakuten_0725.json', encoding='utf-8'))
today = datetime.date.today().isoformat()
ng = []
print('構築', len(rows), '件\n')
for e in rows:
    p = []
    if not e.get('venue') or e['venue'].strip() in ('', '全国ツアー（）'):
        p.append('会場が空')
    if '（）' in (e.get('venue') or '') or '（）' in (e.get('dateLabel') or ''):
        p.append('空カッコ')
    if not e.get('tickets'):
        p.append('枠なし')
    for t in e.get('tickets', []):
        if t['date'] < today:
            p.append('締切が過去:%s' % t['type'][:20])
        if t.get('startDate') and t['startDate'] == t['date'] and not t.get('saleUntilSoldOut'):
            p.append('隠れ枠(単日形)')
        if not re.search(r'（.*\d{1,2}/\d{1,2}.*公演）', t['type']):
            p.append('バッジに公演日が無い:%s' % t['type'][:24])
        if t['date'] > e['date']:
            p.append('締切>公演日')
        if not t.get('url', '').startswith('https://click.linksynergy.com/deeplink'):
            p.append('deeplinkでない')
    if re.search(r'var |jQuery|function|＜|\.\.\.$', (e.get('venue') or '') + (e.get('dateLabel') or '')):
        p.append('ゴミ混入')
    if p:
        ng.append((e['id'], e['name'], p))

if ng:
    print('🚨 要修正 %d件' % len(ng))
    for i, n, p in ng:
        print('  id=%s %s' % (i, n[:40]))
        for x in dict.fromkeys(p):
            print('      -', x)
else:
    print('✅ QC OK（会場/バッジ公演日/締切/隠れ枠/deeplink すべて問題なし）')
