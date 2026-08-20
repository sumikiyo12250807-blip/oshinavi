# -*- coding: utf-8 -*-
"""7/9 新着50件 収集driver（複合bash禁止→python1本化）。
発売前ファースト: 音楽(01) rlsIn=03,04 → 演劇(02) → クラシック(07) → アート(05) → イベント(06)。
各ジャンルをsubprocessで順次ハーベスト(sleepで429回避)→未掲載newを集約→
DB重複(名前+eventCd)除去→50件選定→build_pia_entries入力(cand50)を出力。"""
import re, io, sys, json, time, subprocess, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

JOBS = [
    ('01', 'rlsIn=03', 'music03'),
    ('01', 'rlsIn=04', 'music04'),
    ('02', 'rlsIn=03', 'engeki03'),
    ('07', 'rlsIn=03', 'classic03'),
    ('05', 'rlsIn=03', 'art03'),
    ('06', 'rlsIn=03', 'event03'),
]

def run_harvest(lg, flt, tag):
    out = 'tmp/presale_%s_0710.json' % tag
    try:
        subprocess.run([sys.executable, 'tools/presale_harvest.py', lg, out, flt],
                       capture_output=True, timeout=600)
        d = json.load(open(out, encoding='utf-8'))
        return d.get('new', [])
    except Exception as e:
        print('HARVEST FAIL', tag, e)
        return []

def eventcd(url):
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', url or '')
    return m.group(1) if m else ''

def norm(s):
    s = unicodedata.normalize('NFKC', s)
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—]', '', s).lower()

# existing eventCds in DB
idx = open('index.html', encoding='utf-8').read()
db_cds = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', idx))
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S)
EVENTS = json.loads(m.group(2))
maxid = max(e['id'] for e in EVENTS)

# harvest each genre
buckets = []
for i, (lg, flt, tag) in enumerate(JOBS):
    items = run_harvest(lg, flt, tag)
    print('  %-10s : new=%d' % (tag, len(items)))
    buckets.append((tag, items))
    if i < len(JOBS) - 1:
        time.sleep(6)

# collect in priority order, dedupe by eventCd + norm(name)
seen_cd, seen_nm, selected = set(db_cds), set(), []
for tag, items in buckets:
    def keyf(it):
        r = it.get('rlsdate', '')
        if r in ('', 'TODAY'):
            return (0, '')
        try:
            y, mo, da = [int(x) for x in r.split('/')]
            return (1, '%04d%02d%02d' % (y, mo, da))
        except Exception:
            return (2, r)
    for it in sorted(items, key=keyf):
        cd = eventcd(it['url'])
        nm = norm(it['artist'])
        if not cd or cd in seen_cd or (nm and nm in seen_nm):
            continue
        seen_cd.add(cd); seen_nm.add(nm)
        selected.append((tag, it))
        if len(selected) >= 50:
            break
    if len(selected) >= 50:
        break

cands = []
for n, (tag, it) in enumerate(selected):
    cands.append({'newid': maxid + 1 + n, 'artist': it['artist'], 'urls': [it['url']],
                  '_srcgenre': tag})
json.dump(cands, open('tmp/cand50_0710.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('\n=== 選定 %d件 (id %d..%d) ===' % (len(cands), cands[0]['newid'], cands[-1]['newid']))
from collections import Counter
c = Counter(t for t, _ in selected)
for k, v in c.items():
    print('   %s: %d' % (k, v))
print('--- 一覧 ---')
for tag, it in selected:
    print('  [%s] %s | 発売%s | %s | %s' % (tag, it['artist'][:30], it.get('rlsdate', ''),
                                          it.get('perfdate', '')[:16], it.get('pref', '')))
