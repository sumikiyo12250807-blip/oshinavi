# -*- coding: utf-8 -*-
"""受付中(まだ買える)から新着候補を穴埋めで拾う。発売前の在庫が枯れた日用。

🚨 受付中は「締切が4日先以降」のものだけ（[[feedback_presale_first_harvest]]のコロラリー
   ＝もうじき終わる枠は載せる価値が薄い。ユーザーが「もうじき終わるのばっかり」と不満）。
🚨 ジャンル優先＝音楽 > 演劇 > クラシック > イベント > スポーツ > アート(最後)。

  python tmp/harvest_open_0817.py <件数> <出力json> --merge <既存cand.json>[,<もう1つ>]
"""
import re, io, sys, json, time, datetime, subprocess, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

ARGV = [a for a in sys.argv[1:] if not a.startswith('--')]
WANT = int(ARGV[0]) if ARGV else 30
OUT = ARGV[1] if len(ARGV) > 1 else 'tmp/cand_open.json'
MERGE = []
if '--merge' in sys.argv:
    MERGE = sys.argv[sys.argv.index('--merge') + 1].split(',')

TODAY = datetime.date.today()
STAMP = '%02d%02d' % (TODAY.month, TODAY.day)
JOBS = [('01', 'music'), ('02', 'engeki'), ('07', 'classic'),
        ('06', 'event'), ('03', 'sports'), ('05', 'art')]
GENRE_PRI = {'music': 0, 'engeki': 1, 'classic': 2, 'event': 3, 'sports': 4, 'art': 5}


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—]', '', s).lower()


def eventcd(u):
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', u or '')
    return m.group(1) if m else ''


items = []
for i, (lg, tag) in enumerate(JOBS):
    f = 'tmp/open_%s_%s.json' % (tag, STAMP)
    t0 = time.time()
    try:
        subprocess.run([sys.executable, 'tools/presale_harvest.py', lg, f, 'rlsStatus=0101'],
                       capture_output=True, timeout=2400)
        d = json.load(open(f, encoding='utf-8'))
        new = d.get('new', [])
    except Exception as ex:
        print('  %-9s HARVEST FAIL %s' % (tag, ex)); continue
    for it in new:
        it['_tag'] = tag
    items += new
    print('  %-9s 未掲載 %4d件  (%.0f秒)' % (tag, len(new), time.time() - t0), flush=True)
    if i < len(JOBS) - 1:
        time.sleep(6)

idx = io.open('index.html', encoding='utf-8').read()
db_cds = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', idx))
maxid = max(e['id'] for e in json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S).group(2)))
for f in MERGE:
    try:
        prev = json.load(open(f, encoding='utf-8'))
        for p in prev:
            db_cds |= set(re.findall(r'event(?:Bundle)?Cd=(\w+)', ' '.join(p.get('urls') or [])))
            maxid = max(maxid, p.get('newid', 0))
        print('  --merge %s: 既選 %d件 / id起点 %d' % (f, len(prev), maxid))
    except FileNotFoundError:
        print('  ⚠️ --merge %s が無い' % f)

try:
    _ex = json.load(open('tools/harvest_exclude.json', encoding='utf-8'))
    EXCLUDE = {x['eventCd'] for x in _ex.get('excluded', [])}
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
json.dump(cands, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
import collections
print('\n=== 候補 %d件 → %s (id %d..%d) ===' % (
    len(cands), OUT, cands[0]['newid'] if cands else 0, cands[-1]['newid'] if cands else 0))
print('   ジャンル:', dict(collections.Counter(c['_srcgenre'] for c in cands)))
print('   ※在庫(未掲載ユニーク) %d件 中から選定' % len({eventcd(i['url']) for i in items if eventcd(i['url']) not in db_cds}))
print('\n🚨 締切が近すぎる枠は build 後に除外すること（今日=%s の4日後=%s より前に終わるもの）'
      % (TODAY.isoformat(), (TODAY + datetime.timedelta(days=4)).isoformat()))
