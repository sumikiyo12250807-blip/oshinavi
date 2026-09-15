# -*- coding: utf-8 -*-
"""うんこミュージアム42件（東京・名古屋・横浜×入場期間）を1エントリにまとめる（2026-09-15 夜）
ユーザー「うんこミュージアムひとつにまとめて」
決まり（memory feedback_tour_consolidate / feedback_tour_per_ticket_url / feedback_new_order_array）:
・まとめ役＝id9288（いちばん小さい番号）。date＝最終日・dateLabel＝期間・prefecture＝「東京・愛知・神奈川」
・🚨畳む前に、url が空の枠へ元エントリの links.pia を t.url として焼き込む（しないと全部の枠がまとめ役の売り場に飛ぶ）
・畳んだあと「(券種, 実効URL) の組」が1つも減っていないことを数える（枠の本数だけでは飛び先の破壊が見えない）
・消した41件の番号は NEW_ORDER からも外す → NEW_ORDER とジャンル new のエントリがぴったり一致するか突き合わせる
・ほかのエントリは1文字も変えない（JSONで前後を比べる）／改行は CRLF のまま（newline=''）
使い方: python merge_unko_0915.py
"""
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
KEEP = 9288
PREF_ORDER = {'東京': 0, '愛知': 1, '神奈川': 2}


def events(text):
    return json.loads(re.search(r'  const EVENTS = (\[.*?\]);', text, re.S).group(1))


def new_order(text):
    return json.loads(re.search(r'const NEW_ORDER = (\[[^\]]*\])', text, re.S).group(1))


def eff(e, t):
    return t.get('url') or (e.get('links') or {}).get('pia')


with open(P, encoding='utf-8', newline='') as f:
    text = f.read()
ev = events(text)
us = [e for e in ev if 'うんこミュージアム' in (e.get('name') or '') + (e.get('artist') or '')]
ids = {e['id'] for e in us}
assert KEEP in ids and len(us) == 42, len(us)
pairs_before = {(t['type'], eff(e, t)) for e in us for t in e.get('tickets') or []}
n_tickets = sum(len(e.get('tickets') or []) for e in us)
no_before = new_order(text)
pool_before = {e['id'] for e in ev if e.get('genre') == 'new'}

# まとめ役を作る（枠は元エントリの売り場URLを焼き込んで、公演日→東京・愛知・神奈川の順）
keep = next(e for e in us if e['id'] == KEEP)
tickets = []
for e in us:
    for t in e.get('tickets') or []:
        t2 = dict(t)
        if not t2.get('url'):
            t2['url'] = (e.get('links') or {}).get('pia')
        tickets.append((t2.get('date') or '', PREF_ORDER.get(e.get('prefecture'), 9), t2))
tickets = [t for _, _, t in sorted(tickets, key=lambda x: (x[0], x[1]))]
merged = {
    'id': KEEP,
    'artist': 'うんこミュージアム',
    'name': 'うんこミュージアム TOKYO／NAGOYA／YOKOHAMA BAY',
    'date': max(e['date'] for e in us),
    'dateLabel': '2026年9月11日(金)〜11月30日(月) 東京/愛知/神奈川',
    'venue': 'ダイバーシティ東京 プラザ2F／うんこミュージアム NAGOYA／うんこミュージアム YOKOHAMA BAY',
    'prefecture': '東京・愛知・神奈川',
    'genre': 'kids',
    '_genre': keep.get('_genre'),
    '_extraGenres': keep.get('_extraGenres', []),
    '_piaSub': keep.get('_piaSub'),
    'price': None,
    'links': keep['links'],
    'tickets': tickets,
    'verified': True,
    'verifiedAt': max(e.get('verifiedAt') or '' for e in us),
}
assert merged['date'] == '2026-11-30'
block = ['  ' + ln for ln in json.dumps(merged, ensure_ascii=False, indent=2).split('\n')]
block[-1] = block[-1] + ','

# 行で差し替える（まとめ役の塊を入れ替え、残り41件の塊を消す）
shutil.copyfile(P, 'index.html.bak_0915_unko_merge')
lines = text.split('\r\n')
out, i, removed = [], 0, []
while i < len(lines):
    if lines[i] == '  {' and i + 1 < len(lines) and lines[i + 1].startswith('    "id": '):
        eid = int(lines[i + 1].split(':')[1].strip().rstrip(','))
        j = i
        while not lines[j].startswith('  }'):
            j += 1
        if eid in ids:
            assert lines[j] == '  },', '最後の要素は想定外: %s' % eid
            if eid == KEEP:
                out += block
            else:
                removed.append(eid)
            i = j + 1
            continue
    out.append(lines[i])
    i += 1
new = '\r\n'.join(out)

# NEW_ORDER から消した番号を外す（書き方はそのまま＝数字と「, 」だけを消す）
m = re.search(r'(const NEW_ORDER = \[)([^\]]*)(\])', new)
arr = [int(x) for x in m.group(2).split(',') if x.strip()]
gone_in_order = [x for x in arr if x in removed]
arr2 = [x for x in arr if x not in removed]
new = new[:m.start(2)] + ', '.join(str(x) for x in arr2) + new[m.end(2):]

# 確かめ
ev2 = events(new)
assert len(ev2) == len(ev) - 41, (len(ev), len(ev2))
m2 = next(e for e in ev2 if e['id'] == KEEP)
pairs_after = {(t['type'], eff(m2, t)) for t in m2['tickets']}
assert pairs_after == pairs_before, (pairs_before - pairs_after, pairs_after - pairs_before)
assert len(m2['tickets']) == n_tickets
assert all(t.get('url') for t in m2['tickets'])
others_before = {e['id']: json.dumps(e, ensure_ascii=False, sort_keys=True) for e in ev if e['id'] not in ids}
others_after = {e['id']: json.dumps(e, ensure_ascii=False, sort_keys=True) for e in ev2 if e['id'] != KEEP}
assert others_before == others_after, 'ほかのエントリが変わった'
pool_after = {e['id'] for e in ev2 if e.get('genre') == 'new'}
no_after = new_order(new)
assert new.count('  const NEW_ORDER') == 1 and '新着const NEW_ORDER' not in new
with open(P, 'w', encoding='utf-8', newline='') as f:
    f.write(new)
print('まとめた＝id%d に %d件（消した %d件）／枠 %d本・(券種, 実効URL) の組 %d → %d（同じ）' % (KEEP, len(us), len(removed), n_tickets, len(pairs_before), len(pairs_after)))
print('飛び先の売り場 %d種類' % len({eff(m2, t) for t in m2['tickets']}))
print('NEW_ORDER から外した番号: %s' % gone_in_order)
print('新着プール %d件 → %d件／NEW_ORDER %d件 → %d件' % (len(pool_before), len(pool_after), len(no_before), len(no_after)))
print('NEW_ORDERにあるがプールに無い: %s' % sorted(set(no_after) - pool_after))
print('プールにあるがNEW_ORDERに無い: %s' % sorted(pool_after - set(no_after)))
print('（書く前の食い違い＝NEW_ORDERにあるがプールに無い %s／プールにあるがNEW_ORDERに無い %s）' % (sorted(set(no_before) - pool_before), sorted(pool_before - set(no_before))))
print('予備: index.html.bak_0915_unko_merge')
