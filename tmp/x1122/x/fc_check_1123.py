import sys, re, json, datetime
from collections import defaultdict, Counter
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
E = C.load(open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())
POSTDIR = 'C:/Users/user/oshinavi/tmp/x1122/x/post/'
POSTS = ['mat0%d' % i for i in range(1, 7)] + ['shu01', 'shu02', 'shu03']
PREFS = set('北海道 青森 岩手 宮城 秋田 山形 福島 茨城 栃木 群馬 埼玉 千葉 東京 神奈川 新潟 富山 石川 福井 山梨 長野 岐阜 静岡 愛知 三重 滋賀 京都 大阪 兵庫 奈良 和歌山 鳥取 島根 岡山 広島 山口 徳島 香川 愛媛 高知 福岡 佐賀 長崎 熊本 大分 宮崎 鹿児島 沖縄 配信 全国 海外'.split())
DAYS = {'11/23': '2026-11-23', '11/24': '2026-11-24', '11/25': '2026-11-25'}
PRE_KW = ('先行', 'プレリザーブ', 'プリセール', 'プレオーダー', '抽選', '会員', 'FC', 'ファンクラブ')

def is_pre(tp):
    head = tp.split('（')[0]
    return any(k in head for k in PRE_KW) and '一般' not in head

def tpref(tp, dflt):
    m = re.findall(r'（([^（）\s]+) [^（）]*公演）', tp)
    return m[-1] if m else dflt

def norm(s):
    return re.sub(r'[\s　]', '', str(s or ''))

rows = []
for e in E:
    for t in e.get('tickets') or []:
        sd = t.get('startDate')
        if sd not in DAYS.values():
            continue
        m = re.search(r'(\d{1,2}):(\d{2})発売', t.get('type', ''))
        tm = '%02d:%s' % (int(m.group(1)), m.group(2)) if m else '??'
        rows.append(dict(id=e['id'], day=sd, time=tm, genre=e.get('genre'), artist=e.get('artist'),
                         name=e.get('name'), pref=e.get('prefecture'), type=t.get('type', ''),
                         soldout=bool(t.get('soldout')), pre=is_pre(t.get('type', '')), tpref=tpref(t.get('type', ''), e.get('prefecture'))))

out = []
def P(*a):
    out.append(' '.join(str(x) for x in a))

# weekday check
for md in ('11/23', '11/24', '11/25'):
    d = datetime.date.fromisoformat(DAYS[md])
    P('曜日', md, '月火水木金土日'[d.weekday()])

listed = {}  # post -> list of (day,line,matched rows)
claimed = set()
total = ok = 0
problems = []
for p in POSTS:
    txt = open(POSTDIR + p + '.txt', encoding='utf-8').read()
    day = None
    items = []
    for ln in txt.splitlines():
        h = re.match(r'【(\d+/\d+)\(.+?\)発売】', ln)
        if h:
            day = DAYS.get(h.group(1)); continue
        if ln.startswith('【'):
            day = None; continue
        m = re.match(r'^(\d\d:\d\d(?:・\d\d:\d\d)*) (.+)$', ln)
        if not (m and day):
            continue
        times = m.group(1).split('・')
        rest = m.group(2)
        tag = None
        tm_ = re.search(r'（([^（）]+)）$', rest)
        if tm_:
            tag = tm_.group(1); rest = rest[:tm_.start()]
        prefs = None
        if '／' in rest:
            last = rest.rsplit('／', 1)[1]
            if all(x in PREFS for x in last.split('・')):
                prefs = last.split('・'); rest = rest.rsplit('／', 1)[0]
        name = norm(rest)
        cands = [r for r in rows if r['day'] == day and r['time'] in times]
        hit = [r for r in cands if name and (name == norm(r['artist']) or name == norm(r['name']) or name in norm(r['artist']) or name in norm(r['name']))]
        if not hit:
            hit = [r for r in cands if norm(r['artist']) and norm(r['artist']) in name]
        if not hit:
            # first-segment match
            seg = norm(rest.split('／')[0])
            hit = [r for r in cands if seg and (seg in norm(r['artist']) or seg in norm(r['name']))]
        # presale filter
        if tag and '先行' in tag:
            hp = [r for r in hit if r['pre']]
        else:
            hp = [r for r in hit if not r['pre']]
        if tag and tag not in ('先行',) and '先行' not in tag:
            hp2 = [r for r in hit if tag.replace('受付', '') in r['type'] or tag in r['type']]
            if hp2:
                hp = hp2
        use = hp or hit
        total += 1
        issues = []
        if not hit:
            issues.append('登録に見当たらない')
        else:
            if not hp:
                issues.append('先行/一般の別が合わない types=' + ' | '.join(sorted(set(r['type'] for r in hit))))
            rp = sorted(set(x for r in use for x in str(r['tpref']).split('・')))
            if prefs is not None and sorted(set(prefs)) != rp:
                issues.append('県 post=%s reg=%s' % ('・'.join(prefs), '・'.join(rp)))
            if prefs is None:
                issues.append('県なし(reg=%s)' % '・'.join(rp))
            if all(r['soldout'] for r in use):
                issues.append('全部売り切れ')
        for r in use:
            claimed.add((r['id'], r['day'], r['time'], r['type']))
        items.append((day, ln, use))
        if issues:
            problems.append((p, ln, issues, sorted(set(r['id'] for r in use)), sorted(set(r['type'][:50] for r in use))))
        else:
            ok += 1
    listed[p] = items

P('=== 一覧の行', total, '行中', ok, '行一致（県なし行は不一致扱いせず別記）')
for p, ln, iss, ids, tps in problems:
    P('[%s] %s  => %s  ids=%s' % (p, ln, ' / '.join(iss), ids))
    for t in tps[:6]:
        P('      type:', t)

P('=== 登録にあるのにどの投稿にも無い行（11/24・11/25・artist+時刻+先行）')
for day in ('2026-11-24', '2026-11-25'):
    lk = set()
    for p in POSTS:
        for d, ln, use in listed[p]:
            if d == day:
                for r in use:
                    lk.add((r['time'], norm(r['artist']), r['pre']))
    g = {}
    for r in rows:
        if r['day'] == day:
            k = (r['time'], norm(r['artist']), r['pre'])
            if k not in lk:
                g.setdefault(k, r)
    for k, r in sorted(g.items(), key=lambda kv: (kv[1]['genre'] or '', kv[0])):
        P('  ', day, r['genre'], k[0], r['id'], str(r['artist'])[:40], r['tpref'], '先行' if k[2] else '', '|', r['type'][:40])

# genres per post
for p in POSTS[1:8]:
    g = Counter()
    for day, ln, use in listed[p]:
        for r in use:
            g[r['genre']] += 1
    P('genre', p, dict(g))

# unclaimed on each day
P('=== 登録にあるのにどの投稿にも無い行（11/23）')
seen = set()
for r in rows:
    k = (r['id'], r['day'], r['time'], r['type'])
    if r['day'] == '2026-11-23' and k not in claimed:
        P('  %s %s %s %s／%s %s %s' % (r['genre'], r['time'], r['id'], r['artist'], r['pref'], '先行' if r['pre'] else '一般', '売切' if r['soldout'] else ''), '|', r['type'][:60])

def lines_for(day, genres):
    g = set()
    for r in rows:
        if r['day'] == day and r['genre'] in genres:
            g.add((r['time'], norm(r['artist']), r['pre']))
    return g

P('=== 11/24・11/25 の残り件数（ジャンル別・artist+時刻+先行で1行）')
for p in POSTS[1:8]:
    gs = set()
    for day, ln, use in listed[p]:
        for r in use:
            if r['day'] == '2026-11-23':
                gs.add(r['genre'])
    for day in ('2026-11-24', '2026-11-25'):
        allk = lines_for(day, gs)
        lk = set()
        for d, ln, use in listed[p]:
            if d == day:
                for r in use:
                    lk.add((r['time'], norm(r['artist']), r['pre']))
        P(p, day, 'genres=', sorted(gs), 'all=', len(allk), 'listed=', len(lk & allk), 'rest=', len(allk - lk))
        for k in sorted(allk - lk):
            P('    rest', k)

# 11/23 rest per post
P('=== 11/23 の載っていない行（ジャンル別）')
for p in POSTS[1:8]:
    gs = set(r['genre'] for d, ln, use in listed[p] for r in use if r['day'] == '2026-11-23')
    allk = lines_for('2026-11-23', gs)
    lk = set((r['time'], norm(r['artist']), r['pre']) for d, ln, use in listed[p] if d == '2026-11-23' for r in use)
    P(p, 'all=', len(allk), 'listed=', len(lk & allk), 'rest=', len(allk - lk))

open('C:/Users/user/oshinavi/tmp/x1122/x/fc_check_1123_result.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('done', total, ok, len(problems))
