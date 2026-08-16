# -*- coding: utf-8 -*-
"""新着候補ハーベスタ（朝ルーチン用・1コマンド）。

  python tools/harvest_new.py [件数] [出力json] [rlsIn] [--merge 既存cand.json]
     例: python tools/harvest_new.py 100 tmp/cand_0711.json
         python tools/harvest_new.py 30 tmp/cand_04.json 04 --merge tmp/cand_03.json

ぴあの発売前(rlsIn=03)を全ジャンルからスイープし、**カウントダウンの価値が高い順**に選ぶ。

第3引数で rlsIn を切り替えられる（03＝30日以内に発売／04＝それより先）。
発売前の在庫が枯れている日は 03 を取り切ったあと 04 を足す（2026-08-17 追加）。
--merge は「同じ日に別スイープで既に選んだ候補」のファイル。そこに入っている eventCd を
重複除外に足し、newid の起点もその続きにする＝2回に分けて回しても id が衝突しない。

【選定順】(2026-07-10 ユーザー指摘で修正)
  旧: 発売日が近い順＋「本日発売/発売日不明」を最優先 → 本日発売ばかり50件埋まり、
      「発売までカウントダウンして教える」というOSHINAVIの主旨と真逆だった。
  新: 4日後以降(遠い順=まだまだ先を優先) > 2〜3日後 > 明日 > 本日発売 > 発売日不明

出力は build_pia_entries.py にそのまま食わせられる cand 形式。
"""
import re, io, sys, json, time, datetime, subprocess, unicodedata, collections

sys.stdout.reconfigure(encoding='utf-8')
ARGV = [a for a in sys.argv[1:] if not a.startswith('--')]
WANT = int(ARGV[0]) if len(ARGV) > 0 else 50
OUT = ARGV[1] if len(ARGV) > 1 else 'tmp/cand_new.json'
RLSIN = ARGV[2] if len(ARGV) > 2 else '03'
MERGE = None
if '--merge' in sys.argv:
    MERGE = sys.argv[sys.argv.index('--merge') + 1]
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
    if n is None: return 4       # 発売日不明
    if n >= 4:    return 0       # ★カウントダウンの価値大
    if n >= 2:    return 1
    if n == 1:    return 2       # 明日発売
    return 3                     # 本日発売


def eventcd(url):
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', url or '')
    return m.group(1) if m else ''


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—]', '', s).lower()


items = []
for i, (lg, tag) in enumerate(JOBS):
    f = f'tmp/presale_{tag}{RLSIN}_{STAMP}.json'
    t0 = time.time()
    try:
        subprocess.run([sys.executable, 'tools/presale_harvest.py', lg, f, f'rlsIn={RLSIN}'],
                       capture_output=True, timeout=1800)
        d = json.load(open(f, encoding='utf-8'))
        new = d.get('new', [])
    except Exception as e:
        print(f'  {tag:<9} HARVEST FAIL {e}'); continue
    for it in new:
        it['_tag'] = tag
    items += new
    print(f'  {tag:<9} 未掲載 {len(new):>4}件  ({time.time()-t0:.0f}秒)')
    if i < len(JOBS) - 1:
        time.sleep(6)          # 429回避

idx = open('index.html', encoding='utf-8').read()
db_cds = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', idx))
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S)
maxid = max(e['id'] for e in json.loads(m.group(2)))

# --merge＝同じ日に別スイープで既に選んだ候補。eventCd を重複除外に足し、id の起点も続きにする。
merged_cds = set()
if MERGE:
    try:
        prev = json.load(open(MERGE, encoding='utf-8'))
        for p in prev:
            merged_cds |= set(re.findall(r'event(?:Bundle)?Cd=(\w+)', ' '.join(p.get('urls') or [])))
            maxid = max(maxid, p.get('newid', 0))
        print(f'  --merge {MERGE}: 既選 {len(prev)}件 / 除外eventCd {len(merged_cds)}件 / id起点 {maxid}')
    except FileNotFoundError:
        print(f'  ⚠️ --merge {MERGE} が無い')
db_cds |= merged_cds

# ジャンル優先度（ユーザー指示 2026-07-10 夜）：音楽 > 演劇 > クラシック > イベント > スポーツ > アート(最後)。
GENRE_PRI = {'music': 0, 'engeki': 1, 'classic': 2, 'event': 3, 'sports': 4, 'art': 5}


def sortkey(x):
    d = days_until(x.get('rlsdate', ''))
    b = bucket(d)
    g = GENRE_PRI.get(x.get('_tag', ''), 9)
    # ①カウントダウン価値のbucket ②ジャンル優先度 ③bucket0は遠い順(降順)・他は近い順。
    # ユーザー指示 2026-07-12(遠い順) + 2026-07-10(ジャンル優先度)。
    return (b, g, -(d or 0) if b == 0 else (d or 0))


# 「調べた上で対象外」と決めた eventCd は二度と拾わない（毎回ハーベストに出てきて
# 毎回同じ判断をやり直す無駄を止める）。理由と決定日は tools/harvest_exclude.json に残す。
# ⚠️ここに入れてよいのは調査済みのものだけ。「分からないから外す」はダメ
# （[[feedback_investigate_dont_guess]]／[[feedback_oshikatsu_first]]）。
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
    seen_cd.add(cd); seen_nm.add(nm)
    sel.append(it)
    if len(sel) >= WANT:
        break

cands = [{'newid': maxid + 1 + n, 'artist': it['artist'],
          # 旧ドメイン ticket.pia.jp/pia/event.do は build が読めない。正規化しておく。
          'urls': [it['url'].replace('ticket.pia.jp/pia/event.do', 't.pia.jp/pia/event/event.do')],
          '_srcgenre': it['_tag']} for n, it in enumerate(sel)]
json.dump(cands, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

NAMES = {0: '4日後以降', 1: '2〜3日後', 2: '明日発売', 3: '本日発売', 4: '発売日不明'}
bc = collections.Counter(bucket(days_until(it.get('rlsdate', ''))) for it in sel)
print(f'\n=== 候補 {len(cands)}件 → {OUT} (id {cands[0]["newid"]}..{cands[-1]["newid"]}) ===' if cands else '候補ゼロ')
for b in sorted(bc):
    print(f'   {NAMES[b]}: {bc[b]}件')
print(f'   ジャンル: {dict(collections.Counter(it["_tag"] for it in sel))}')
print(f'   ※在庫(未掲載ユニーク) {len({eventcd(it["url"]) for it in items})}件 中から選定')
if n_ex:
    # 黙って落とすと「そもそも出てこなかった」のか「除外した」のか分からなくなる。
    print(f'   ※除外リスト(tools/harvest_exclude.json)で {n_ex}件スキップ')
