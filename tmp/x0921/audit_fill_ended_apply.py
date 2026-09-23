# -*- coding: utf-8 -*-
"""印付きの18件（tmp/x0921/audit_fill_ended_built.json）を index.html に入れる（2026-09-21）。
足し込み（名前がそっくり同じ既存エントリが1つ）:
  YAMATO String Quartet 3件 → id2912 / センダイガールズプロレスリング 5件 → id2626
  東京スカパラダイスオーケストラ 2件 → id4236 / 「ドラゴンクエスト」ウインドオーケストラコンサート → id2500
新規（genre new ＋ NEW_ORDER）:
  八神純子 ヤガ祭り the 8th（id801は「八神純子 コンサート 2026」＝別の興行）
  大阪プロレス（同名エントリが3つ＝公演ごとのエントリ・1つに決まらない）
  反田恭平 10th / 尾高忠明 大阪フィル「悲愴」/ ジョン・ウィリアムズ吹奏楽 / TOKYO WIND SPECIAL / 辻本玲＆伊東裕
使い方: python tmp/x0921/audit_fill_ended_apply.py [--apply]
"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
built = {e['id']: e for e in json.load(io.open('tmp/x0921/audit_fill_ended_built.json', encoding='utf-8'))}
MERGE = {950000: 2912, 950001: 2912, 950002: 2912,
         950003: 2626, 950004: 2626, 950005: 2626, 950006: 2626, 950007: 2626,
         950010: 4236, 950011: 4236, 950018: 2500}
NEW = [950008, 950009, 950014, 950015, 950019, 950020, 950022]
assert set(MERGE) | set(NEW) == set(built)
# 辻本玲の抽選カード（ぴあ表記「辻本玲／伊東裕〔東京〕」抽選受付終了）＝券種名が名前に削られたので「抽選」にする
for t in built[950022]['tickets']:
    if t['type'].startswith('辻本玲（'):
        t['type'] = t['type'].replace('辻本玲（', '抽選（', 1)

h = io.open(P, encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))
by = {e['id']: e for e in EV}
nm, ns = 0, 0
for k, dst in MERGE.items():
    e = by[dst]
    have = {(t.get('type'), t.get('url')) for t in e['tickets']}
    for t in built[k]['tickets']:
        assert not t.get('_alive')
        if (t['type'], t['url']) in have:
            print('  既にある', dst, t['type']); continue
        e['tickets'].append(dict(t)); nm += 1
        print('足し込み id%d %s ← %s %s' % (dst, e['name'][:20], t['type'], 'SE' if t.get('saleEnded') else 'SO'))
nid = max(e['id'] for e in EV) + 1
new = []
for k in NEW:
    e = json.loads(json.dumps(built[k]))
    assert e['genre'] == 'new' and e['tickets']
    for t in e['tickets']:
        assert not t.get('_alive')
    e['id'] = nid; nid += 1
    new.append(e); ns += len(e['tickets'])
    print('新規 id%d %s 枠%d' % (e['id'], e['name'][:34], len(e['tickets'])))
EV.extend(new)
ids = [e['id'] for e in new]
print('足し込み %d枠（%d件へ）／新規 %d件 %d枠' % (nm, len(set(MERGE.values())), len(new), ns))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)'); sys.exit(0)
mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
merged = cur + [i for i in ids if i not in cur]
h2, n = re.subn(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', lambda mm: mm.group(1) + '[' + ', '.join(map(str, merged)) + ']', h, count=1)
assert n == 1
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)
arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\n', NL)
io.open(P, 'w', encoding='utf-8', newline='').write(h2[:m.start()] + m.group(1) + arr + m.group(3) + h2[m.end():])
print('書き込み完了 新規ids=%s NEW_ORDER %d→%d' % (ids, len(cur), len(merged)))
