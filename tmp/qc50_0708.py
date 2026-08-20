# -*- coding: utf-8 -*-
"""7/8 新着49件のQC: 文字化け/全角残り/空カッコ/日付整合/同一アーティスト(ツアーまとめ候補)。"""
import re, json, io, sys, unicodedata
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
pool = [e for e in EVENTS if e.get('genre') == 'new']
print('新着プール genre:new =', len(pool))

FW = re.compile(r'[Ａ-Ｚａ-ｚ０-９｡-ﾟ]')  # 全角英数・半角カナ(（）〜・は保護対象なので除外)
def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/（）()「」『』【】’\'"!！\-—~〜]', '', s).lower()

print('\n===== 各件ダンプ =====')
for e in sorted(pool, key=lambda x: x['id']):
    print('id=%d [%s] %s' % (e['id'], e.get('_genre', '?'), e['artist']))
    print('   dL: %s' % e.get('dateLabel', ''))
    print('   venue=%s / pref=%s / date=%s' % (e.get('venue', ''), e.get('prefecture', ''), e.get('date', '')))
    for t in e['tickets']:
        print('    - %s (%s)' % (t['type'], t['date']))

print('\n===== ⚠️ フラグ =====')
# 1) 全角/半角カナ残り
for e in pool:
    hit = []
    if FW.search(e['artist']): hit.append('artist')
    if FW.search(e.get('venue', '')): hit.append('venue')
    for t in e['tickets']:
        if FW.search(t['type']): hit.append('ticket:%s' % t['type'][:14])
    if hit:
        print('  [全角残り] id=%d %s -> %s' % (e['id'], e['artist'][:24], hit))
# 2) 空カッコ 全国ツアー（）
for e in pool:
    if re.search(r'（\s*）|\(\s*\)', e.get('venue', '')):
        print('  [空カッコ] id=%d %s venue=%s' % (e['id'], e['artist'][:20], e['venue']))
# 3) 日付整合: ticket.date が dateLabel/date と極端にズレ or 2027表記
for e in pool:
    # 2027公演なのに dateLabel に年表記(2027/令和9/R9)が無い
    is2027 = (e.get('date', '') >= '2027') or any(t['date'] >= '2027' for t in e['tickets'])
    dl = e.get('dateLabel', '')
    if is2027 and ('2027' not in dl and '令和9' not in dl and 'R9' not in dl):
        print('  [2027年表記なし?] id=%d %s dL=%s' % (e['id'], e['artist'][:20], dl))
    # ticket.date が全て過去(<今日)なら発売前でない疑い
    if all(t['date'] < '2026-07-08' for t in e['tickets']):
        print('  [全ticket過去?] id=%d %s' % (e['id'], e['artist'][:20]))
# 4) 同一(正規化)アーティスト = ツアーまとめ候補
g = defaultdict(list)
for e in pool:
    g[norm(e['artist'])].append(e)
# 既存DB(new以外)にも同名がいれば統合候補
db = defaultdict(list)
for e in EVENTS:
    if e.get('genre') != 'new':
        db[norm(e['artist'])].append(e)
print('\n===== 🔗 ツアーまとめ候補(プール内同名) =====')
found = False
for k, es in g.items():
    if len(es) > 1:
        found = True
        print('  同名 %d件: %s' % (len(es), ' / '.join('id%d(%s)' % (e['id'], e.get('prefecture', '')) for e in es)))
if not found:
    print('  なし')
print('\n===== 🔗 既存DBに同名あり(重複/統合注意) =====')
found = False
for e in pool:
    k = norm(e['artist'])
    if k in db:
        found = True
        print('  id=%d %s <-> 既存 %s' % (e['id'], e['artist'][:24],
              ' '.join('id%d' % d['id'] for d in db[k][:4])))
if not found:
    print('  なし')
