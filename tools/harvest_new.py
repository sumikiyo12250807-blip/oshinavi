# -*- coding: utf-8 -*-
"""新着候補ハーベスタ（朝ルーチン用・1コマンド）。

  python tools/harvest_new.py [件数] [出力json]
     例: python tools/harvest_new.py 100 tmp/cand_0711.json

ぴあの発売前(rlsIn=03)を全ジャンルからスイープし、**カウントダウンの価値が高い順**に選ぶ。

【選定順】(2026-07-10 ユーザー指摘で修正)
  旧: 発売日が近い順＋「本日発売/発売日不明」を最優先 → 本日発売ばかり50件埋まり、
      「発売までカウントダウンして教える」というOSHINAVIの主旨と真逆だった。
  新: 4日後以降(近い順) > 2〜3日後 > 明日 > 本日発売 > 発売日不明

出力は build_pia_entries.py にそのまま食わせられる cand 形式。
"""
import re, io, sys, json, time, datetime, subprocess, unicodedata, collections

sys.stdout.reconfigure(encoding='utf-8')
WANT = int(sys.argv[1]) if len(sys.argv) > 1 else 50
OUT = sys.argv[2] if len(sys.argv) > 2 else 'tmp/cand_new.json'
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
    f = f'tmp/presale_{tag}03_{STAMP}.json'
    t0 = time.time()
    try:
        subprocess.run([sys.executable, 'tools/presale_harvest.py', lg, f, 'rlsIn=03'],
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

seen_cd, seen_nm, sel = set(db_cds), set(), []
for it in sorted(items, key=lambda x: (bucket(days_until(x.get('rlsdate', ''))),
                                       days_until(x.get('rlsdate', '')) or 0)):
    cd, nm = eventcd(it['url']), norm(it['artist'])
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
