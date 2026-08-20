# -*- coding: utf-8 -*-
"""X投稿の候補出し（Opus担当・機械抽出／ネットもトークンも使わない）。
memory: feedback_model_routing_fable の3段分担①・feedback_x_pick_bigname_miss の判定軸
  強い＝ボカロ/ゲーム/アニメ/VTuber・YouTuber/若手ロック/アイドル・K-POP/2.5次元
  弱い＝クラシック企画公演・オーケストラ・宝塚・シニア歌謡・器楽ホール公演
X投稿は「発売開始(発売前)」を告知する（feedback_x_deadline_vs_presale_by_genre）。
"""
import re, json, sys, datetime, collections
sys.stdout.reconfigure(encoding='utf-8')

TODAY = datetime.date.today()
h = open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))

posted = {r.get('title') or '' for r in json.load(open('tools/x_log.json', encoding='utf-8'))['posts']}

STRONG = {'anime', 'vtuber', 'youtuber', 'idol', 'kpop', '2.5ji', 'seiyuu', 'rock', 'fanevent'}
WEAK = {'classic', 'enka', 'dento', 'dinnershow', 'art', 'gourmet', 'kaigai'}

rows = []
for e in EV:
    g = e.get('genre')
    if g in ('new',):
        continue
    for t in e.get('tickets') or []:
        sd = t.get('startDate')
        if not sd:
            continue
        try:
            d = datetime.date.fromisoformat(sd)
        except ValueError:
            continue
        n = (d - TODAY).days
        if not (1 <= n <= 4):        # 明日〜4日後の発売開始
            continue
        if t.get('soldout') or t.get('saleEnded'):
            continue
        rows.append({
            'id': e['id'], 'name': e.get('name'), 'artist': e.get('artist'),
            'genre': g, 'extra': e.get('extraGenres') or [],
            'sale': sd, 'in_days': n, 'type': t.get('type'),
            'pref': e.get('prefecture'), 'venue': e.get('venue'),
            'showdate': e.get('dateLabel'), 'posted': (e.get('name') or '') in posted,
        })

# 同一エントリは1行に（いちばん早い発売枠）
best = {}
for r in rows:
    k = r['id']
    if k not in best or r['sale'] < best[k]['sale']:
        best[k] = r
rows = sorted(best.values(), key=lambda r: (r['sale'], r['id']))

print('明日〜4日後に発売開始する枠を持つエントリ:', len(rows), '件')
print('発売日の内訳:', dict(collections.Counter(r['sale'] for r in rows)))
print('ジャンル内訳:', dict(collections.Counter(r['genre'] for r in rows)))

def bucket(r):
    gs = {r['genre']} | set(r['extra'])
    if gs & STRONG:
        return 'A強'
    if gs & WEAK:
        return 'C弱'
    return 'B中'

for tag in ('A強', 'B中', 'C弱'):
    sel = [r for r in rows if bucket(r) == tag]
    print('\n' + '=' * 20, tag, len(sel), '件')
    for r in sel:
        mark = '📌既出' if r['posted'] else '    '
        print('%s id%-5s [%s%s] %s発売(あと%d日)' % (
            mark, r['id'], r['genre'], ('+' + ','.join(r['extra'])) if r['extra'] else '',
            r['sale'], r['in_days']))
        print('        %s' % (r['name'] or '')[:60])
        print('        %s ／ %s' % ((r['pref'] or ''), (r['venue'] or '')[:52]))
        print('        枠: %s' % (r['type'] or '')[:64])
