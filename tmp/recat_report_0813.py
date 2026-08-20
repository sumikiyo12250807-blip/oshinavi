# -*- coding: utf-8 -*-
import io, json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
rows = json.load(io.open('tmp/engeki_recat.json', encoding='utf-8'))

chg = [r for r in rows if r.get('new_genre') and r['new_genre'] != 'engeki']
print('=== ジャンルが変わる %d件 ===' % len(chg))
for g in ['musical', 'dento', 'classic', 'owarai', 'kids', 'yougaku', 'art']:
    sel = [r for r in chg if r['new_genre'] == g]
    if not sel:
        continue
    print('\n--- → %s (%d件) ---' % (g, len(sel)))
    for r in sel:
        print('  %d\t[ぴあ:%s]\t%s' % (r['id'], r['sub'], (r['name'] or '')[:44]))

nog = [r for r in rows if not r.get('new_genre')]
print('\n=== 機械で決められない %d件（触らない）===' % len(nog))
for k, v in collections.Counter(r['note'] for r in nog).most_common():
    print('  %-34s %3d' % (k, v))
print('\n--- カテゴリが取れなかった分の名前（先頭25件）---')
for r in [r for r in nog if 'カテゴリ取れず' in (r['note'] or '')][:25]:
    print('  %d\t%s' % (r['id'], (r['name'] or '')[:48]))
print('\n--- 未収載カテゴリの中身 ---')
for r in [r for r in nog if '未収載' in (r['note'] or '')]:
    print('  %d\t[%s]\t%s' % (r['id'], r['sub'], (r['name'] or '')[:44]))
