# -*- coding: utf-8 -*-
"""まとめ枠7本の素材（明日10/2のリスト＝機械・予告5件＝箱の大きさで選んだ行）を tmp/x1001/x/material_posts.md に書く。
 10/2はお笑い44件（100件に届かない）＝全部並べる（X_SCRIPT 0番の2026-09-26訂正）。"""
import io, json, sys
sys.path.insert(0, 'tmp/x1001/x')
src = open('tmp/x1001/x/material_1002.py', encoding='utf-8').read()
ns = {}
exec(src[:src.index("out = io.open(")], ns)
POSTS = [
 ('post04', 'お笑い・落語', ['owarai']),
 ('post05', 'J-POP・ロック・歌い手・K-POP', ['jpop', 'rock', 'utaite', 'vtuber', 'anime', 'fes', 'kpop', 'yougaku']),
 ('post06', 'アイドル', ['idol']),
 ('post07', 'クラシック・演歌・ジャズ・ディナーショー', ['classic', 'enka', 'dento', 'jazz', 'dinnershow']),
 ('post08', 'スポーツ', ['sports']),
 ('post09', 'ミュージカル・演劇・トークショー', ['musical', 'engeki', 'aisatsu', 'talkshow', 'seiyuu', '2.5ji', 'movie']),
 ('post10', 'キッズ・ファンイベント・イベント・展覧会・ダンス・その他', ['dance', 'kids', 'fanevent', 'event', 'art', 'hanabi', 'musicetc', 'gakusai', 'circus', 'magic', 'douyou', 'gourmet']),
]
FUT = json.load(io.open('tmp/x1001/x/future_pick.json', encoding='utf-8'))
rows = ns['collect']('2026-10-02', True)
out = io.open('tmp/x1001/x/material_posts.md', 'w', encoding='utf-8')
out.write('# 10/2(金)発売 まとめ枠7本の素材（リストは機械で作ってある＝行はそのまま使う・並べ替えない）\n\n')
for key, title, gs in POSTS:
    rr = [r for r in rows if r[4].get('genre') in gs]
    g = ns['group'](rr)
    out.write('## %s ＝ %s\n\n' % (key, title))
    out.write('【10/2(金)発売】（%d行）\n' % len(g))
    for k, v in g.items():
        out.write(ns['line'](k, v) + '\n')
    out.write('\n')
    for d, lab in (('2026-10-03', '10/3(土)'), ('2026-10-04', '10/4(日)')):
        f = FUT[key][d]
        if not f['lines']:
            continue
        out.write('【%s発売】\n' % lab)
        for l in f['lines']:
            out.write(l + '\n')
        if f['rest']:
            out.write('他にも%sあるわ。\n' % f['rest'])
        out.write('\n')
    out.write('\n')
out.close()
print('ok')
