# -*- coding: utf-8 -*-
"""新着投入後の二段構えQC（機械側）。
 ① eventCd 重複（新着 vs 既存）        [[feedback_harvest_dedup_check]]
 ② 正規化名の一致（全角/半角を吸収）
 ③ 同一エントリ内で同じバッジ文字列が2枚以上 [[feedback_newpool_fullwidth_halfwidth]]
 ④ 全角ラテン/全角数字の残り（表記ゆれ）
 ⑤ バッジ形式（公演日が完全M/D形で（…公演）内にあるか）
 ⑥ 千秋楽 date と ticket の整合・verified 欠落
"""
import json, re, sys, unicodedata, collections
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
news = [e for e in EVENTS if e.get('genre') == 'new']
olds = [e for e in EVENTS if e.get('genre') != 'new']
print('新着 %d件 / 既存 %d件' % (len(news), len(olds)))


def cds(e):
    s = set()
    for u in [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets') or []]:
        for mm in re.finditer(r'event(?:Bundle)?Cd=(\w+)', u or ''):
            s.add(mm.group(1))
    return s


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/「」『』（）()【】\'"!！\-—~〜～．.]', '', s).lower()


old_cd = {}
for e in olds:
    for c in cds(e):
        old_cd.setdefault(c, []).append(e['id'])
old_name = collections.defaultdict(list)
for e in olds:
    old_name[norm(e.get('artist') or e.get('name'))].append(e['id'])

print('\n--- ① eventCd 重複 ---')
hit = 0
for e in news:
    dup = sorted(c for c in cds(e) if c in old_cd)
    if dup:
        hit += 1
        print('  🚨 id=%d %s ← 既存 %s と同じ eventCd %s' % (
            e['id'], e['name'][:34], old_cd[dup[0]], dup))
print('  重複 %d件' % hit)

print('\n--- ② 正規化名の一致（別公演のこともある・要目視） ---')
hit = 0
for e in news:
    k = norm(e.get('artist') or e.get('name'))
    if k in old_name:
        hit += 1
        print('  ⚠️ id=%d %s ← 既存 %s と同名' % (e['id'], e['name'][:34], old_name[k]))
print('  同名 %d件' % hit)

print('\n--- ③ 同一エントリ内の重複バッジ文字列 ---')
hit = 0
for e in news:
    c = collections.Counter(t['type'] for t in e.get('tickets') or [])
    for t, n in c.items():
        if n > 1:
            hit += 1
            print('  🚨 id=%d %s ×%d  %s' % (e['id'], e['name'][:26], n, t))
print('  重複バッジ %d件' % hit)

print('\n--- ④ 全角ラテン/全角数字の残り ---')
FW = re.compile(r'[Ａ-Ｚａ-ｚ０-９]')
hit = 0
for e in news:
    fields = [('name', e.get('name')), ('artist', e.get('artist')),
              ('venue', e.get('venue')), ('dateLabel', e.get('dateLabel'))]
    fields += [('ticket', t['type']) for t in e.get('tickets') or []]
    bad = [(k, v) for k, v in fields if v and FW.search(v)]
    if bad:
        hit += 1
        print('  ⚠️ id=%d %s' % (e['id'], bad[:2]))
print('  全角残り %d件' % hit)

print('\n--- ⑤ バッジ形式NG ---')
hit = 0
for e in news:
    for t in e.get('tickets') or []:
        if not re.search(r'（[^）]*\d{1,2}/\d{1,2}[^）]*公演）', t['type']):
            hit += 1
            print('  🚨 id=%d %s | %s' % (e['id'], e['name'][:26], t['type']))
print('  形式NG %d枠' % hit)

print('\n--- ⑥ verified欠落 / date整合 ---')
hit = 0
for e in news:
    if not e.get('verified'):
        hit += 1
        print('  🚨 id=%d verified なし' % e['id'])
    for t in e.get('tickets') or []:
        if not t.get('date'):
            hit += 1
            print('  🚨 id=%d 枠にdateなし %s' % (e['id'], t['type']))
print('  不備 %d件' % hit)

print('\n--- 参考: 新着のジャンル下書き内訳 ---')
c = collections.Counter(e.get('_genre') or '(空)' for e in news)
print('  ' + ' / '.join('%s%d' % kv for kv in c.most_common()))
print('  _piaSub 空 or その他 =',
      [e['id'] for e in news if not e.get('_piaSub') or 'その他' in (e.get('_piaSub') or '')])
