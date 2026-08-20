# -*- coding: utf-8 -*-
"""新着50件(id4226-4275)の投入後QC。
 ①全角ラテン/数字の残存 ②同一バッジ文字列の重複 ③公演日欠落 ④_piaSub未マップ
 （memory: feedback_newpool_fullwidth_halfwidth / feedback_badge_date_full_form / project_vendor_genre_autoassign）"""
import re, json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
new = [e for e in EV if 4226 <= e.get('id', 0) <= 4275]
print('対象', len(new), '件')

FW = re.compile(r'[Ａ-Ｚａ-ｚ０-９]')
fw = []
for e in new:
    for k in ('artist', 'name', 'venue', 'dateLabel'):
        if FW.search(e.get(k) or ''):
            fw.append((e['id'], k, e.get(k)))
    for t in e.get('tickets') or []:
        if FW.search(t.get('type') or ''):
            fw.append((e['id'], 'ticket.type', t.get('type')))
print('① 全角ラテン/数字の残存', len(fw))
for r in fw[:15]:
    print('   ', r)

dupbadge = []
for e in new:
    c = collections.Counter((t.get('type') or '') for t in (e.get('tickets') or []))
    for k, v in c.items():
        if v > 1:
            dupbadge.append((e['id'], e.get('name'), k, v))
print('② 同一バッジ文字列の重複', len(dupbadge))
for r in dupbadge:
    print('   ', r)

MD = re.compile(r'\d{1,2}/\d{1,2}')
noday = [(e['id'], e.get('name'), t.get('type'))
         for e in new for t in (e.get('tickets') or [])
         if '公演' in (t.get('type') or '') and not MD.search(t.get('type') or '')]
print('③ バッジ内の公演日欠落', len(noday))
for r in noday[:10]:
    print('   ', r)

print('④ ジャンル下書きの内訳')
g = collections.Counter(e.get('_genre') for e in new)
for k, v in sorted(g.items(), key=lambda x: -x[1]):
    print('   ', k, v)
print('   _piaSub 未取得/その他:')
for e in new:
    s = e.get('_piaSub') or ''
    if (not s) or ('その他' in s):
        print('     id%s _piaSub=%r _genre=%s %s' % (e['id'], s, e.get('_genre'), (e.get('name') or '')[:40]))
print('   参考: _piaSub 一覧')
for k, v in collections.Counter(e.get('_piaSub') for e in new).most_common():
    print('     %-28s %d' % (k, v))

print('⑤ verified/genre')
print('   genre!=new:', [e['id'] for e in new if e.get('genre') != 'new'])
print('   verified!=True:', [e['id'] for e in new if e.get('verified') is not True])
print('⑥ NEW_ORDER件数', len(json.loads(re.search(r'const NEW_ORDER = (\[.*?\]);', h, re.S).group(1))))
