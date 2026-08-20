# -*- coding: utf-8 -*-
"""rlsIn=04（発売が30日より先）も足して候補を組み直す。
理由＝rlsIn=03の在庫が枯れて「本日発売」44/46になった（harvest_new は rlsIn=03 固定）。
カウントダウンの価値が高い順に並べる規則は tools/harvest_new.py と同一
（bucket / GENRE_PRI / sortkey / EXCLUDE / eventCd＆正規化名の重複除外）。
"""
import collections
import datetime
import json
import re
import subprocess
import sys
import time
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')

WANT = int(sys.argv[1]) if len(sys.argv) > 1 else 50
OUT = sys.argv[2] if len(sys.argv) > 2 else 'tmp/cand_0730b.json'
TODAY = datetime.date.today()
STAMP = f'{TODAY:%m%d}'

JOBS = [('01', 'music'), ('02', 'engeki'), ('07', 'classic'),
        ('05', 'art'), ('06', 'event'), ('03', 'sports')]


def days_until(r):
    if not r or r == 'TODAY':
        return 0
    m = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', r)
    if not m:
        return None
    return (datetime.date(*[int(x) for x in m.groups()]) - TODAY).days


def bucket(n):
    if n is None: return 4
    if n >= 4:    return 0
    if n >= 2:    return 1
    if n == 1:    return 2
    return 3


def eventcd(url):
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', url or '')
    return m.group(1) if m else ''


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—]', '', s).lower()


items = []
# ① 既に取れている rlsIn=03 の結果を再利用（さっき回したもの）
for lg, tag in JOBS:
    f = f'tmp/presale_{tag}03_{STAMP}.json'
    try:
        d = json.load(open(f, encoding='utf-8'))
    except Exception:
        continue
    for it in d.get('new', []):
        it['_tag'] = tag
        it['_sweep'] = '03'
        items.append(it)
print(f'rlsIn=03 再利用: {len(items)}件')

# ② rlsIn=04（発売がもっと先）を新規スイープ
for i, (lg, tag) in enumerate(JOBS):
    f = f'tmp/presale_{tag}04_{STAMP}.json'
    t0 = time.time()
    try:
        subprocess.run([sys.executable, 'tools/presale_harvest.py', lg, f, 'rlsIn=04'],
                       capture_output=True, timeout=1800)
        d = json.load(open(f, encoding='utf-8'))
        new = d.get('new', [])
    except Exception as e:
        print(f'  {tag:<9} rlsIn=04 HARVEST FAIL {e}')
        continue
    for it in new:
        it['_tag'] = tag
        it['_sweep'] = '04'
    items += new
    print(f'  {tag:<9} rlsIn=04 未掲載 {len(new):>4}件  ({time.time()-t0:.0f}秒)')
    if i < len(JOBS) - 1:
        time.sleep(6)

idx = open('index.html', encoding='utf-8').read()
db_cds = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', idx))
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S)
maxid = max(e['id'] for e in json.loads(m.group(2)))

GENRE_PRI = {'music': 0, 'engeki': 1, 'classic': 2, 'event': 3, 'sports': 4, 'art': 5}


def sortkey(x):
    d = days_until(x.get('rlsdate', ''))
    b = bucket(d)
    g = GENRE_PRI.get(x.get('_tag', ''), 9)
    return (b, g, -(d or 0) if b == 0 else (d or 0))


try:
    _ex = json.load(open('tools/harvest_exclude.json', encoding='utf-8'))
    EXCLUDE = {x['eventCd'] for x in _ex.get('excluded', [])}
except FileNotFoundError:
    EXCLUDE = set()

seen_cd, seen_nm, sel = set(db_cds), set(), []
n_ex = 0
for it in sorted(items, key=sortkey):
    cd, nm = eventcd(it['url']), norm(it['artist'])
    if cd in EXCLUDE:
        n_ex += 1
        continue
    if not cd or cd in seen_cd or (nm and nm in seen_nm):
        continue
    seen_cd.add(cd)
    seen_nm.add(nm)
    sel.append(it)
    if len(sel) >= WANT:
        break

cands = [{'newid': maxid + 1 + n, 'artist': it['artist'],
          'urls': [it['url'].replace('ticket.pia.jp/pia/event.do', 't.pia.jp/pia/event/event.do')],
          '_srcgenre': it['_tag']} for n, it in enumerate(sel)]
json.dump(cands, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

NAMES = {0: '4日後以降', 1: '2〜3日後', 2: '明日発売', 3: '本日発売', 4: '発売日不明'}
bc = collections.Counter(bucket(days_until(it.get('rlsdate', ''))) for it in sel)
print(f'\n=== 候補 {len(cands)}件 → {OUT} (id {cands[0]["newid"]}..{cands[-1]["newid"]}) ===' if cands else '候補ゼロ')
for b in sorted(bc):
    print(f'   {NAMES[b]}: {bc[b]}件')
print(f'   ジャンル: {dict(collections.Counter(it["_tag"] for it in sel))}')
print(f'   スイープ別: {dict(collections.Counter(it["_sweep"] for it in sel))}')
print(f'   ※在庫(未掲載ユニーク) {len({eventcd(it["url"]) for it in items})}件 中から選定')
if n_ex:
    print(f'   ※除外リストで {n_ex}件スキップ')
