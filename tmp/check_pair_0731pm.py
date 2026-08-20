# -*- coding: utf-8 -*-
"""新着同士の重複疑い（同名・同eventCd）を洗う＋新着49件の一覧を出す。"""
import json, re, sys, unicodedata, collections
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
news = [e for e in EVENTS if e.get('genre') == 'new']


def cds(e):
    s = set()
    for u in [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets') or []]:
        for mm in re.finditer(r'event(?:Bundle)?Cd=(\w+)', u or ''):
            s.add(mm.group(1))
    return s


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/「」『』（）()【】\'"!！\-—~〜～．.]', '', s).lower()


print('--- 新着同士の eventCd 重複 ---')
seen = {}
for e in news:
    for c in cds(e):
        seen.setdefault(c, []).append(e['id'])
dups = {c: v for c, v in seen.items() if len(v) > 1}
print('  ', dups if dups else 'なし')

print('--- 新着同士の同名 ---')
byname = collections.defaultdict(list)
for e in news:
    byname[norm(e.get('artist') or e.get('name'))].append(e['id'])
same = {k: v for k, v in byname.items() if len(v) > 1}
print('  ', {k[:30]: v for k, v in same.items()} if same else 'なし')

print('\n--- 新着49件 ---')
for e in news:
    t0 = min(t['date'] for t in e['tickets'])
    print('%d  %-46s %s %s  枠%d  最早%s  _genre=%s%s' % (
        e['id'], e['name'][:46], e['prefecture'], e['dateLabel'][:22],
        len(e['tickets']), t0, e.get('_genre'),
        '  ⚠️_piaSub=' + (e.get('_piaSub') or '空') if not e.get('_piaSub') or 'その他' in (e.get('_piaSub') or '') else ''))
