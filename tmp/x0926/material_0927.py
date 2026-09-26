# -*- coding: utf-8 -*-
"""9/25(金)発売のX投稿の素材を作る（2026-09-23 夜）。
X_SCRIPT の本数の決め方＝①トレンド枠0〜1本 ②主役枠3本（Xフォロワー上位3組）③残りはジャンル別まとめ。
出力:
  tmp/x0926/material_top.md   … トレンド枠＋主役3本の素材（Fableに渡す）
  tmp/x0926/material.md       … まとめ枠の素材（ジャンル別・明日発売は全部／2〜3日後は大物5件＋丸めた件数）
🚨件数は「全部載せた時」だけ実数。丸めるのは rough()（X_SCRIPT 3番）。
"""
import io
import json
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
TOM = '2026-09-27'
D2 = '2026-09-28'
D3 = '2026-09-29'

# 主役3組（2026-09-23 ブラウザ実測のフォロワー順）
STAR = [
    (20272, 'GAG CONTE LIVE「THIS AND THAT」', 640900, '@saraba_morita（2026-09-26 実測・さらば青春の光 森田哲矢 本人）'),
    (11111, '新日本プロレス', 482400, '@njpw1972（2026-09-26 実測・団体公式）'),
    (19168, '金属・黒帯のダルガラミ', 278300, '@kinzokutomoyasu（2026-09-26 実測・金属バット友保）'),
]
TREND = []  # 9/26 17:xx トレンド8位に在庫0＝トレンド枠なし #   # 9/25 17:04のトレンド8位は在庫0件（渡辺翔太は同名の別人）＝トレンド枠なし

h = io.open('index.html', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
by_id = {e['id']: e for e in EVENTS}


def slots_on(ev, day):
    out = []
    for t in ev.get('tickets') or []:
        if t.get('soldout') or t.get('saleEnded'):
            continue
        if t.get('startDate') == day:
            out.append(t)
    return out


def live_slots(ev):
    return [t for t in (ev.get('tickets') or []) if not t.get('soldout') and not t.get('saleEnded')]


def rough(n):
    # X_SCRIPT 3番（2026-09-13）＝下1桁0〜4は切り下げて「◯件以上」／5〜9は切り上げて「◯件近く」／10未満はそのまま
    if n < 10:
        return '%d件' % n
    base = (n // 10) * 10
    if n - base <= 4:
        return '%d件以上' % base
    return '%d件近く' % (base + 10)


top = io.open('tmp/x0926/material_top.md', 'w', encoding='utf-8')
top.write('# 9/27(日)発売 X投稿の素材（トレンド枠＋主役3本）\n\n')
top.write('🚨ここに書いてある事実だけで書くこと。経歴・音楽的特徴・人気度・フォロワー数は書かない。\n')
top.write('🚨「先行」は条件を満たした人だけの枠＝一般発売と同じに書かない。\n\n')

top.write('## ① トレンド枠＝なし（9/26 17:2xのXトレンド8位までは在庫に当たる名前0件）\n\n')
for i in TREND:
    e = by_id.get(i)
    if not e:
        continue
    lk = {k: v for k, v in (e.get('links') or {}).items() if v}
    top.write('- **%s**（id%s）\n  会場: %s\n  日付: %s\n  売り場: %s\n' % (
        e.get('name') or e.get('artist'), i, e.get('venue'), e.get('dateLabel'), ','.join(lk.keys())))
    for t in live_slots(e):
        top.write('    ・%s\n' % t.get('type'))
    top.write('\n')

top.write('## ②〜④ 主役枠（Xフォロワーが多い上位3組・9/26発売）\n\n')
for i, name, fo, note in STAR:
    e = by_id.get(i)
    if not e:
        top.write('- ⚠️ id%s が見つからない\n' % i)
        continue
    lk = {k: v for k, v in (e.get('links') or {}).items() if v}
    top.write('### %s（id%s）\n' % (name, i))
    top.write('- 公演: %s\n- 会場: %s\n- 売り場: %s\n' % (e.get('dateLabel'), e.get('venue'), ','.join(lk.keys())))
    top.write('- **9/27に始まる枠**:\n')
    for t in slots_on(e, TOM):
        top.write('    ・%s\n' % t.get('type'))
    other = [t for t in live_slots(e) if t.get('startDate') != TOM]
    if other:
        top.write('- 同じエントリの他の枠（参考・本文に入れるかは中身しだい）:\n')
        for t in other[:12]:
            top.write('    ・%s\n' % t.get('type'))
    top.write('\n')
# ヤクルトは車椅子席が別エントリ・ラグビーは同じ大会が3エントリ
for extra, why in ((20265, 'かまいたち 大阪（別エントリ）'),):
    e2 = by_id.get(extra)
    if e2:
        top.write('※%s＝id%s（%s／%s）\n' % (why, extra, e2.get('dateLabel'), e2.get('venue')))
        for t in slots_on(e2, TOM):
            top.write('    ・%s\n' % t.get('type'))
top.close()

# まとめ枠
star_ids = {i for i, _, _, _ in STAR} | {20265} | set(TREND)
by_genre = defaultdict(list)
future = defaultdict(list)
for e in EVENTS:
    if e.get('genre') == 'new':
        continue
    for t in live_slots(e):
        sd = t.get('startDate')
        if sd == TOM and e['id'] not in star_ids:
            by_genre[e.get('genre') or '?'].append((t.get('type'), e))
        elif sd in (D2, D3):
            future[sd].append((t.get('type'), e))

mat = io.open('tmp/x0926/material.md', 'w', encoding='utf-8')
mat.write('# 9/27(日)発売 X投稿の素材（ジャンル別まとめ枠）\n\n')
mat.write('🚨1投稿＝1ジャンル。明日発売はそのジャンルを**全部**載せる（一部だけだと「うちの推しは無い」と閉じられる）。\n')
mat.write('🚨1行＝1アーティスト（同じ時刻の地域は「・」でまとめる）。時刻を行頭に置く。\n')
mat.write('🚨主役3組（関連エントリ込み）はここから外してある（別の投稿で出すため）。\n\n')


def hhmm(ty):
    m = re.search(r'(\d{1,2}):(\d{2})\s*発売', ty or '')
    return '%02d:%s' % (int(m.group(1)), m.group(2)) if m else '(時刻なし)'


for g in sorted(by_genre, key=lambda k: -len(by_genre[k])):
    rows = by_genre[g]
    mat.write('## %s（%d枠）\n' % (g, len(rows)))
    for ty, e in sorted(rows, key=lambda r: hhmm(r[0])):
        mat.write('- %s %s／%s id%s\n    %s\n' % (
            hhmm(ty), e.get('artist') or e.get('name'), e.get('prefecture'), e['id'], ty))
    mat.write('\n')

mat.write('\n# 2〜3日後の発売（予告として1投稿に5件くらい＋丸めた件数）\n')
mat.write('🚨5件の選び方＝**大物＝箱の大きさ（会場のキャパ）**で選ぶ。並びは時刻順のまま。\n\n')
for d in (D2, D3):
    rows = future[d]
    mat.write('## %s（%d枠）\n' % (d, len(rows)))
    for ty, e in sorted(rows, key=lambda r: hhmm(r[0])):
        mat.write('- %s %s／%s（%s）id%s\n' % (hhmm(ty), e.get('artist') or e.get('name'),
                                              e.get('prefecture'), (e.get('venue') or '')[:28], e['id']))
    mat.write('→ 5件だけ載せるなら残りは「%s」\n\n' % rough(max(0, len(rows) - 5)))
mat.close()
print('wrote tmp/x0926/material_top.md, tmp/x0926/material.md')
print('まとめ枠のジャンル数=%d / 明日の枠=%d' % (len(by_genre), sum(len(v) for v in by_genre.values())))
