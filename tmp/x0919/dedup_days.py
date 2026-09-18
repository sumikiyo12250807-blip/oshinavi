# -*- coding: utf-8 -*-
"""pia_days_list の「未登録」を**県＋公演日＋名前**で当て直して、見かけの抜けを外す（2026-09-18 夜）。

🚨 pia_days_list は eventCd で当てるので、ぴあが同じ公演を別の売り場番号で出していると
   「未登録」に化ける（[[feedback_existing_entries_miss_new_windows]]＝未登録はeventCdでなく県＋公演日で当てる）。
   ここでは登録側の「その発売日の枠」を名前でひいて、**本当に無い分だけ**残す。

  python tmp/x0919/dedup_days.py tmp/x0919/pia_days_01.txt
"""
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
PATH = sys.argv[1]

h = io.open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\'’]', '', s)


# 登録側＝(正規化した名前) -> {その枠の発売日}
byname = {}
for e in EV:
    k = norm(e.get('artist') or e.get('name'))
    if not k:
        continue
    d = byname.setdefault(k, {'ids': set(), 'starts': set(), 'genre': set()})
    d['ids'].add(e['id'])
    d['genre'].add(e.get('genre'))
    for t in e.get('tickets') or []:
        if t.get('startDate'):
            d['starts'].add(t['startDate'])

rows = [l.rstrip('\n') for l in io.open(PATH, encoding='utf-8') if l.startswith('  20')]
real, fake = [], []
for l in rows:
    m = re.match(r'\s*(\d{4}-\d{2}-\d{2}) (.*?) \| (.*?) \| (.*?) \| (.*)$', l)
    if not m:
        continue
    iso, artist, saletype, venue, tail = m.groups()
    k = norm(artist)
    d = byname.get(k)
    if d and iso in d['starts']:
        fake.append((iso, artist, 'id%s に同じ発売日の枠あり（売り場番号が違うだけ）'
                     % ','.join(str(x) for x in sorted(d['ids']))))
    else:
        real.append((iso, artist, saletype, venue, tail,
                     ('名前一致 id%s（その発売日の枠なし）' % ','.join(str(x) for x in sorted(d['ids'])))
                     if d else '名前の一致も無し'))

o = io.open(PATH.replace('.txt', '_real.txt'), 'w', encoding='utf-8')
o.write('本当の抜け %d件 ／ 見かけ（同じ発売日の枠が既にある）%d件\n\n' % (len(real), len(fake)))
for iso, a, st, ven, tail, note in real:
    o.write('%s %s | %s | %s\n    %s\n    %s\n' % (iso, a, st, ven, tail, note))
o.write('\n=== 見かけ（足さない）===\n')
for iso, a, note in fake:
    o.write('%s %s ｜%s\n' % (iso, a, note))
o.close()
print('本当の抜け %d / 見かけ %d → %s' % (len(real), len(fake), PATH.replace('.txt', '_real.txt')))
