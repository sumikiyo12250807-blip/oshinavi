# -*- coding: utf-8 -*-
# 11/10(火)発売 お笑いまとめ動画の spec（Suno『わらいのちけっと』58.8 秒・エレクトロスウィング 約133BPM・50年代レトロの子 9 ポーズ・背景＝緑〜青の波 104570）
#   matome1109o/make_spec.py の形：歌詞は塊（最大5行）を小節の頭で入れ替え・本物のOSHINAVIはサビのタップ場面だけ（50254 M-1グランプリ2026 準々決勝）
#   時刻は transcribe2（lyrics_times2.txt）の言葉の頭。字幕の文言は USLT に合わせる（名前はサイトの表記）
#   🚨 字は縮めない（11/3 すちこ）＝1行が 960px に入らない時は同じ大きさのまま2行に折る（コロコロチキチキ／ペッパーズ）。下で全行の幅を測って止める
import io, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124l/'
CHUNKS = [
    [('11月+24日の', [2.5, 3.2]), ('発売の', [4.5]), ('ライブの', [5.2])],
    [('チケット', [5.7]), ('言うわよ', [6.3])],
    [('朝 10時', [7.2, 8.5]), ('奇妙礼太郎BAND と', [9.9, 12.0])],
    [('在日ファンク 東京', [12.1, 13.2])],
    [('11時', [14.2]), ('DEEN 北海道', [15.0, 15.9]), ('先行', [16.8])],
    [('夕方 6時', [19.1, 20.0]), ('惡ノ夢と', [20.5]), ('暇潰シ 東京', [21.6, 22.2])],
    [('夜 9時', [23.3, 23.7]), ('東京アイドル劇場', [24.0]), ('東京 きゅ〜くる', [25.8, 26.6])],
    [('夜 10時すぎ', [27.3, 28.0]), ('革命-DOPENESS-', [29.3]), ('たち 東京', [30.8, 31.2])],
    [('忘れないでね', [33.0])],
    [('売り場まで', [35.2]), ('案内+するのは', [37.2, 37.8]), ('おしなび', [38.5])],
    [('公演と', [39.3]), ('アーティストの', [40.1]), ('紹介も 載せてるわ', [41.1, 42.1])],
    [('oshinavi+.jp', [43.5, 44.6]), ('だわ', [46.1])],   # すちこ 11/13「検索するのは小文字だから小文字で表示して」
]
LOW = {9, 10}
DUR = 51.62
B = json.load(io.open(D + 'beats.json'))
BTS = B['beats']
bar = 4 * 60 / B['bpm']

sys.path.insert(0, 'tools')
import oshimade_mv as M
from PIL import Image, ImageDraw
_d = ImageDraw.Draw(Image.new('RGB', (1, 1)))
_over = []
for c in CHUNKS:
    for r, _ in c:
        w = _d.textlength(r.replace('+', ''), font=M.font(96))
        if w > 960:
            _over.append((r, int(w)))
assert not _over, ('960px に入らない行（縮めずに折ること）', _over)


def toks(row, tt):
    out = []
    for w in row.split(' '):
        parts = w.split('+')
        for j, p in enumerate(parts):
            out.append([p, None, j == len(parts) - 1])
    assert len(out) == len(tt), (row, tt)
    for o, x in zip(out, tt):
        o[1] = x
    out[-1][2] = False
    return out


lines = [[toks(r, tt) for r, tt in c] for c in CHUNKS]
starts = [c[0][0][1] for c in lines]
PH = min(range(4), key=lambda p: sum(min(abs(BTS[i] - s) for i in range(p, len(BTS), 4)) for s in starts))
BARS = [BTS[i] for i in range(PH, len(BTS), 4)]
chunks = []
for n, c in enumerate(lines):
    s = c[0][0][1]
    prev_last = lines[n - 1][-1][-1][1] + 0.25 if n else 0.0
    cand = [b for b in BARS if prev_last <= b <= s + 0.05]
    show = max(cand) if cand else max(prev_last, s - 0.3)
    chunks.append({'show': round(show, 3), 'lines': c, 'low': n in LOW})
for n, c in enumerate(chunks):
    last = c['lines'][-1][-1][1]
    c['hide'] = chunks[n + 1]['show'] if n + 1 < len(chunks) else round(DUR - 0.05, 3)
    if n + 1 < len(chunks) and c['hide'] - last > 2 * bar + 0.5:
        c['hide'] = round(last + 2 * bar, 3)
# 11/10：この曲は後奏がほとんど無い（歌い終わり 57.0 秒・曲の終わり 58.8 秒）＝最後の塊「OSHINAVI.jp／なのよ」は終わりまで出しておく

CHORUS_AT, URL_AT = chunks[9]['show'], chunks[11]['show']   # 11/14 「公演とアーティストの紹介も載せてるわ／売り場まで案内するのは おしなび」＝タップの場面・「OSHINAVI.jp なのよ」から締め
chunks[11]['cy'] = 1080   # 11/13 締め「OSHINAVI.jp／だわ」は少し上＝下の段の4人（1260〜1490）の頭に重ねない
# 前奏（0〜4.1 秒）も真ん中を空けない＝「明日 11/10(火)／発売の お笑い」を白で出しておく（なぞらない）
if chunks[0]['show'] > 1.0:   # 11/11 歌い出し 0.5 秒＝前奏の塊は要らない（最初の塊が 0.17 秒から出ている）
    chunks.insert(0, {'show': 0.3, 'hide': chunks[0]['show'], 'lines': [[['ライブ', 999, False]], [['11/24(火)', 999, True], ['発売', 999, False]]], 'low': False})
SHOTS = {'badge': {'img': D + 'cards/screen_badge.png', 'crop': [0, 0, 1080, 1920], 'boxes': [], 'title': '発売日のバッジをタップ', 'tap': True}}
SCENES = [[0.0, 'shot:dj_title'], [CHORUS_AT, 'shot:badge'], [URL_AT, 'shot:dj_url'], [DUR, 'shot:dj_url']]
karaoke = [{'start': c['show'], 'end': c['hide'], 'lines': [''.join(w + (' ' if s else '') for w, _, s in r) for r in c['lines']], 'times': []} for c in chunks]
S = {'when': '11/24(火) 発売', 'kind': 'ライブ',   # 「クラシック・おでかけ」は下の札の幅に入らず両端が切れた（11/20 絵コンテ） 'name': '奇妙礼太郎BAND／在日ファンク',
     'out': D + 'out.mp4', 'song': D + 'song.mp3', 'posedir': D + 'poses',
     'dur': DUR, 'beat': 60 / B['bpm'], 'calm': True, 'fade_in': 0.0, 'fade_out': 1.5,
     'scenes': SCENES, 'karaoke': karaoke, 'chunks': chunks, 'panels': [[0.0, 1]], 'poses': [[0.0, 'r1']], 'blocks': {}, 'shots': SHOTS,
     'kara_size': 96, 'kara_y': 1000, 'kara_w': 960, 'kara_maxl': 5,
     'kara_col': {'done': [255, 228, 0], 'todo': [255, 255, 255], 'stroke': [20, 10, 40]},
     'shot_w': 600, 'shot_top': 250}
io.open(D + 'music_1123.json', 'w', encoding='utf-8').write(json.dumps(S, ensure_ascii=False, indent=1))
print('PH', PH, 'bar', round(bar, 3))
print('chunks', [(c['show'], c['hide']) for c in chunks])
