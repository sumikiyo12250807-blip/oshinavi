# -*- coding: utf-8 -*-
"""【選定ロジック修正版】カウントダウン価値の高い順に新着候補を選ぶ。

旧: rlsdate が '' or 'TODAY' を最優先(0)→ 本日発売ばかり50件埋まる（OSHINAVIの主旨と真逆）
新: 発売まで4日以上ある子を先に、次に2〜3日、明日、最後に本日発売。
    ぴあ発売前リスト(rlsIn=03)は30日以内しか出ないので、それ以上先は取れない。
    ※ rlsdate='' はぴあが本日発売のとき時刻しか書かない形 [[reference_pia_today_sale_timeonly]]

ぴあは叩かない（収集済み tmp/presale_*_0710.json を選び直すだけ）。
"""
import re, io, sys, json, glob, unicodedata, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TODAY = datetime.date(2026, 7, 10)
WANT = int(sys.argv[1]) if len(sys.argv) > 1 else 50

def days_until(r):
    if not r or r == 'TODAY':
        return 0
    m = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', r)
    if not m:
        return None
    return (datetime.date(*[int(x) for x in m.groups()]) - TODAY).days

def bucket(n):
    if n is None: return 4          # 発売日不明
    if n >= 4:    return 0          # ★カウントダウンの価値大
    if n >= 2:    return 1
    if n == 1:    return 2          # 明日発売
    return 3                        # 本日発売

def eventcd(url):
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', url or '')
    return m.group(1) if m else ''

def norm(s):
    s = unicodedata.normalize('NFKC', s)
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—]', '', s).lower()

idx = open('index.html', encoding='utf-8').read()
db_cds = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', idx))
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S)
EVENTS = json.loads(m.group(2))
maxid = max(e['id'] for e in EVENTS)

items = []
for f in sorted(glob.glob('tmp/presale_*_0710.json')):
    tag = re.search(r'presale_(.+?)_0710', f).group(1)
    for it in json.load(open(f, encoding='utf-8')).get('new', []):
        it['_tag'] = tag
        items.append(it)

seen_cd, seen_nm, sel = set(db_cds), set(), []
for it in sorted(items, key=lambda x: (bucket(days_until(x.get('rlsdate', ''))),
                                       days_until(x.get('rlsdate', '')) or 0)):
    cd = eventcd(it['url'])
    nm = norm(it['artist'])
    if not cd or cd in seen_cd or (nm and nm in seen_nm):
        continue
    seen_cd.add(cd); seen_nm.add(nm)
    sel.append(it)
    if len(sel) >= WANT:
        break

cands = [{'newid': maxid + 1 + n, 'artist': it['artist'],
          'urls': [it['url'].replace('ticket.pia.jp/pia/event.do', 't.pia.jp/pia/event/event.do')],
          '_srcgenre': it['_tag']} for n, it in enumerate(sel)]
json.dump(cands, open('tmp/cand_countdown_0710.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

from collections import Counter
bc = Counter(bucket(days_until(it.get('rlsdate', ''))) for it in sel)
NAMES = {0: '4日後以降', 1: '2〜3日後', 2: '明日発売', 3: '本日発売', 4: '発売日不明'}
print(f'=== 選定 {len(cands)}件 (id {cands[0]["newid"]}..{cands[-1]["newid"]}) ===')
for b in sorted(bc): print(f'   {NAMES[b]}: {bc[b]}件')
print(f'   ジャンル: {dict(Counter(it["_tag"] for it in sel))}')
print('\n--- 一覧（発売日順）---')
for it in sel:
    n = days_until(it.get('rlsdate', ''))
    print(f'  [{it["_tag"]:<10}] 発売まであと{n:>2}日 ({it.get("rlsdate","本日")}) | {it["artist"][:28]} | {it.get("pref","")}')
