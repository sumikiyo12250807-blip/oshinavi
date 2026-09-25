# -*- coding: utf-8 -*-
"""週末の記事「今週のピックアップ」の候補を出す（毎週金曜・2026-09-25 ユーザー指示で定着）。

  python tools/pickup_cands.py            # 次の月〜日
  python tools/pickup_cands.py 2026-09-28 2026-10-04
"""
import io, json, re, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import datetime
# 引数なし＝次の月曜〜日曜（金曜に回して日曜号の候補を出す）／引数あり＝FROM TO（YYYY-MM-DD）
if len(sys.argv) >= 3:
    FROM, TO = sys.argv[1], sys.argv[2]
else:
    _t = datetime.date.today()
    _mon = _t + datetime.timedelta(days=(7 - _t.weekday()) % 7 or 7)
    FROM, TO = _mon.isoformat(), (_mon + datetime.timedelta(days=6)).isoformat()
print('対象', FROM, '〜', TO)
src = io.open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
BIG = re.compile(r'ドーム|アリーナ|スタジアム|武道館|城ホール|ガーデンシアター|国際フォーラム|さいたまスーパー|ぴあアリーナ|Kアリーナ|横浜BUNTAI|代々木|幕張|ベルーナ|ゼビオ|グリーンアリーナ|ワールド記念|マリンメッセ|きたえーる|セキスイハイム|サンドーム|Zepp|フェスティバルホール|NHKホール|東京体育館|有明')
by = collections.defaultdict(lambda: {'slots': 0, 'ids': set(), 'genre': '', 'prefs': set(), 'venues': set(), 'big': set(), 'days': set(), 'new': False})
for e in EV:
    hit = [t for t in e.get('tickets') or [] if not t.get('soldout') and not t.get('saleEnded') and FROM <= (t.get('startDate') or '') <= TO and re.search(r'\d{1,2}:\d{2}発売', t.get('type') or '')]
    if not hit:
        continue
    a = re.sub(r'\s*(20\d\d|２０２６).*$', '', e.get('artist') or '').strip() or e.get('artist')
    r = by[a]
    r['slots'] += len(hit); r['ids'].add(e['id']); r['genre'] = e.get('_genre') if e.get('genre') == 'new' else e.get('genre')
    r['new'] = r['new'] or e.get('genre') == 'new'
    for t in hit:
        m = re.search(r'（([^（）]*?) ', t['type'])
        if m: r['prefs'].update(m.group(1).split('・'))
        r['days'].add(t['startDate'][5:])
    v = e.get('venue') or ''
    r['venues'].add(v)
    for b in BIG.findall(v): r['big'].add(b)
rows = sorted(by.items(), key=lambda kv: (-len(kv[1]['big']) * 2 - kv[1]['slots'], kv[0]))
out = []
for a, r in rows:
    if r['slots'] >= 3 or r['big']:
        out.append('%s\t%s\t枠%d\t県%d\t発売日%s\t大箱:%s\tid%s%s' % (a, r['genre'], r['slots'], len(r['prefs']), ','.join(sorted(r['days'])), '・'.join(sorted(r['big'])) or '-', ','.join(map(str, sorted(r['ids']))), '（新着）' if r['new'] else ''))
io.open('tmp/pickup0920/cands.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(len(out))
print('\n'.join(out))
