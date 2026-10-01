# -*- coding: utf-8 -*-
# 深掘りの候補探し：10/5〜10/11に発売が始まる枠を持つ振り分け済みエントリのうち、
#   会期が長い（dateLabel の最初〜最後が14日以上）か、展覧会・ミュージカル・演劇・イベント・キッズ・アニメ系のもの → deep_cands.txt
import io, json, re, datetime
root = 'C:/Users/user/oshinavi/'
s = io.open(root + 'index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', s)
E, _ = json.JSONDecoder().raw_decode(s, m.start(1))
A, B = '2026-10-05', '2026-10-11'
DONE = ('コーラスライン', 'ドラゴンクエスト', 'ドラクエ', '禅とジブリ')
GEN = {'art', 'musical', 'engeki', 'event', 'kids', 'anime', '2.5ji', 'circus', 'magic', 'gourmet', 'hanabi', 'fes', 'movie', 'classic', 'dento', 'hougaku'}
def span(lab):
    ds = re.findall(r'(\d{4})年(\d{1,2})月(\d{1,2})日', lab or '')
    if len(ds) < 2:
        return 0
    a = datetime.date(*map(int, ds[0])); b = datetime.date(*map(int, ds[-1]))
    return (b - a).days
rows = []
for e in E:
    if e.get('genre') == 'new':
        continue
    if not any(A <= (t.get('startDate') or '') <= B for t in e.get('tickets') or []):
        continue
    name = (e.get('name') or '')
    if any(d in name for d in DONE):
        continue
    sp = span(e.get('dateLabel'))
    g = e.get('genre')
    if sp >= 14 or g in GEN:
        sd = sorted({t['startDate'] for t in e['tickets'] if A <= (t.get('startDate') or '') <= B})
        rows.append((sp, g, e['id'], name[:50], (e.get('venue') or '')[:30], (e.get('dateLabel') or '')[:40], ','.join(x[5:] for x in sd)))
rows.sort(key=lambda r: (-r[0], r[1]))
out = io.open(root + 'tmp/pickup1004/deep_cands.txt', 'w', encoding='utf-8')
out.write('%d件\n' % len(rows))
for r in rows:
    out.write('%3d日 [%s] id%s %s | %s | %s | 発売%s\n' % r)
