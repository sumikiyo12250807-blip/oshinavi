# -*- coding: utf-8 -*-
"""X投稿の素材を「投稿の束ごと」に整える（2026-09-02 夜の便）。
1エントリ1行に畳んで（同じ枠が公演ごとに何本もあるため）、時刻順に並べる。

🚨束はサイトのジャンルグループ（index.html の GENRE_GROUPS）に合わせる。
   自分で勝手に束ねると取りこぼす（2026-09-01＝fes/kids を入れ忘れて9/4の4件が落ちた）。
   music だけは大きいので「音楽」と「クラシック」に割る（classic/jazz がクラシック側）。
出力は tmp/x_material_0902.txt。
"""
import collections, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

DAYS = {'2026-09-03': '明日9/3(木)', '2026-09-04': '9/4(金)', '2026-09-05': '9/5(土)'}

BUCKET = [
    ('音楽', {'jpop', 'rock', 'enka', 'idol', 'kpop', 'yougaku', 'anime',
              'hiphop', 'chanson', 'hougaku', 'musicetc'}),
    ('クラシック', {'classic', 'jazz'}),
    ('舞台', {'engeki', 'musical', 'dento', 'seiyuu', '2.5ji', 'circus'}),
    ('エンタメ', {'owarai', 'kaidan', 'dinnershow', 'aisatsu', 'youtuber',
                  'vtuber', 'fanevent', 'magic'}),
    ('おでかけ', {'sports', 'art', 'kids', 'fes', 'hanabi', 'gourmet', 'gakusai'}),
]

# e+ 由来の新着プールは _genre を持たないので束が決まらない。中身を見て入れ先を決めたもの。
# 🚨これは「X投稿でどの束に並べるか」だけの話で、エントリのジャンルは変えていない。
# 24件とも会場がライブハウス／ホールの音楽公演だった（2026-09-02 実物を1件ずつ確認）。
NEWMAP = {
    5989: '音楽', 5996: '音楽', 6001: '音楽', 6008: '音楽', 6009: '音楽', 6014: '音楽',
    6015: '音楽', 6016: '音楽', 6021: '音楽', 6040: '音楽', 6045: '音楽', 6047: '音楽',
    6048: '音楽', 6053: '音楽', 6054: '音楽', 6055: '音楽', 6062: '音楽', 6063: '音楽',
    6065: '音楽', 6066: '音楽', 6069: '音楽', 6183: '音楽', 6193: '音楽', 6197: '音楽',
}

src = open('index.html', encoding='utf-8').read()
PREFS = set(re.findall(
    r'"([^"]+)":\s*"(?:hokkaido|tohoku|kanto|chubu|kinki|chugoku|shikoku|kyushu|kaigai)"', src))
EVENTS = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', src, re.S).group(1))

G2B = {}
for b, gs in BUCKET:
    for g in gs:
        G2B[g] = b

data = collections.defaultdict(lambda: collections.defaultdict(dict))
unbucketed = collections.Counter()
for e in EVENTS:
    g = e.get('genre') or ''
    b = (NEWMAP.get(e['id']) or G2B.get(e.get('_genre') or '')) if g == 'new' else G2B.get(g)
    for t in e.get('tickets', []):
        if t.get('soldout'):
            continue
        sd = t.get('startDate')
        if sd not in DAYS:
            continue
        m = re.search(r'(\d{1,2})/(\d{1,2})\s+(\d{1,2}:\d{2})発売', t.get('type', ''))
        if not m:
            continue
        if not b:                      # 束が決まらない＝落ちる。必ず数えて報告する
            unbucketed[(sd, e['id'], e.get('artist', '')[:34], (e.get('venue') or '')[:26])] += 1
            continue
        hhmm = m.group(3)
        pm = re.search(r'（([^（）]*?)\s+(?:R\d年\s*)?\d{1,2}/\d{1,2}', t.get('type', ''))
        pref = (pm.group(1).strip() if pm and pm.group(1).strip() else (e.get('prefecture') or ''))
        if pref not in PREFS and re.sub(r'(都|府|県)$', '', pref) in PREFS:
            pref = re.sub(r'(都|府|県)$', '', pref)
        senko = bool(re.match(r'^(?!一般)(.*(先行|プレリザーブ|プリセール|抽選|次受付))', t['type']))
        key = re.sub(r'\s+', '', e.get('artist', ''))
        cur = data[sd][b].get(key)
        if cur is None:
            data[sd][b][key] = {'time': hhmm, 'artist': e.get('artist', ''), 'prefs': {pref},
                                'senko': senko, 'show': e.get('date', ''),
                                'venue': e.get('venue', ''), 'id': e['id']}
        else:
            cur['prefs'].add(pref)
            cur['time'] = min(cur['time'], hhmm)
            cur['senko'] = cur['senko'] and senko

out = []
for sd in DAYS:
    out.append('\n' + '#' * 72)
    out.append('# %s に発売開始' % DAYS[sd])
    out.append('#' * 72)
    for b, _ in BUCKET:
        lst = data[sd].get(b) or {}
        if not lst:
            continue
        out.append('\n【%s】%d組' % (b, len(lst)))
        for r in sorted(lst.values(), key=lambda x: (x['time'], x['artist'])):
            p = '・'.join(sorted(x for x in r['prefs'] if x))
            tag = '（先行）' if r['senko'] else ''
            out.append('  %s %s／%s%s   [id%s / 公演%s / %s]'
                       % (r['time'], r['artist'], p, tag, r['id'], r['show'], r['venue'][:28]))
if unbucketed:
    out.append('\n\n🚨束が決まらず落ちた枠（要確認）')
    for (sd_, i, nm, vn), c in sorted(unbucketed.items()):
        out.append("  %s id%s %s ／ %s ×%d枠" % (sd_, i, nm, vn, c))
else:
    out.append('\n\n束が決まらず落ちた枠＝0（取りこぼしなし）')
open('tmp/x_material_0902.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('wrote tmp/x_material_0902.txt')
for sd in DAYS:
    tot = sum(len(v) for v in data[sd].values())
    print('  %s … %d組（%s）' % (DAYS[sd], tot,
          ' / '.join('%s%d' % (b, len(data[sd].get(b) or {})) for b, _ in BUCKET if data[sd].get(b))))
print('  束が決まらず落ちた枠 =', sum(unbucketed.values()))
