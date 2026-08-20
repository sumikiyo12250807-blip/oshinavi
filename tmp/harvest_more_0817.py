# -*- coding: utf-8 -*-
"""さっき回したスイープ結果（tmp/open_*.json）から追加の候補を選ぶ。
ぴあを二度叩かずに済むよう、キャッシュ済みのJSONだけを使う。

  python tmp/harvest_more_0817.py <件数> <出力json> --merge a.json,b.json,c.json
"""
import re, io, sys, json, glob, unicodedata, collections
sys.stdout.reconfigure(encoding='utf-8')

ARGV = [a for a in sys.argv[1:] if not a.startswith('--')]
WANT = int(ARGV[0]) if ARGV else 20
OUT = ARGV[1] if len(ARGV) > 1 else 'tmp/cand_more.json'
MERGE = sys.argv[sys.argv.index('--merge') + 1].split(',') if '--merge' in sys.argv else []

GENRE_PRI = {'music': 0, 'engeki': 1, 'classic': 2, 'event': 3, 'sports': 4, 'art': 5}


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—]', '', s).lower()


def eventcd(u):
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', u or '')
    return m.group(1) if m else ''


items = []
for f in glob.glob('tmp/open_*_0817.json'):
    tag = re.search(r'open_(\w+?)_0817', f).group(1)
    for it in json.load(io.open(f, encoding='utf-8')).get('new', []):
        it['_tag'] = tag
        items.append(it)
print('キャッシュから %d件（%s）' % (len(items), dict(collections.Counter(i['_tag'] for i in items))))

idx = io.open('index.html', encoding='utf-8').read()
db_cds = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', idx))
maxid = max(e['id'] for e in json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S).group(2)))
for f in MERGE:
    try:
        for p in json.load(io.open(f, encoding='utf-8')):
            db_cds |= set(re.findall(r'event(?:Bundle)?Cd=(\w+)', ' '.join(p.get('urls') or [])))
            maxid = max(maxid, p.get('newid', 0))
    except FileNotFoundError:
        print('  ⚠️ %s が無い' % f)
print('id起点 %d' % maxid)

try:
    EXCLUDE = {x['eventCd'] for x in json.load(io.open('tools/harvest_exclude.json', encoding='utf-8')).get('excluded', [])}
except FileNotFoundError:
    EXCLUDE = set()

seen_cd, seen_nm, sel = set(db_cds), set(), []
for it in sorted(items, key=lambda x: GENRE_PRI.get(x.get('_tag', ''), 9)):
    cd, nm = eventcd(it['url']), norm(it['artist'])
    if not cd or cd in EXCLUDE or cd in seen_cd or (nm and nm in seen_nm):
        continue
    seen_cd.add(cd); seen_nm.add(nm)
    sel.append(it)
    if len(sel) >= WANT:
        break

cands = [{'newid': maxid + 1 + n, 'artist': it['artist'],
          'urls': [it['url'].replace('ticket.pia.jp/pia/event.do', 't.pia.jp/pia/event/event.do')],
          '_srcgenre': it['_tag']} for n, it in enumerate(sel)]
json.dump(cands, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('=== 候補 %d件 → %s (id %d..%d) / %s' % (
    len(cands), OUT, cands[0]['newid'] if cands else 0, cands[-1]['newid'] if cands else 0,
    dict(collections.Counter(c['_srcgenre'] for c in cands))))
