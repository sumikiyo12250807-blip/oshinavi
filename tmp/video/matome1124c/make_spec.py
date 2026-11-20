# -*- coding: utf-8 -*-
# 11/10(火)発売 お笑いまとめ動画の spec（Suno『わらいのちけっと』58.8 秒・エレクトロスウィング 約133BPM・50年代レトロの子 9 ポーズ・背景＝緑〜青の波 104570）
#   matome1109o/make_spec.py の形：歌詞は塊（最大5行）を小節の頭で入れ替え・本物のOSHINAVIはサビのタップ場面だけ（50254 M-1グランプリ2026 準々決勝）
#   時刻は transcribe2（lyrics_times2.txt）の言葉の頭。字幕の文言は USLT に合わせる（名前はサイトの表記）
#   🚨 字は縮めない（11/3 すちこ）＝1行が 960px に入らない時は同じ大きさのまま2行に折る（コロコロチキチキ／ペッパーズ）。下で全行の幅を測って止める
import io, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
CHUNKS = [
    [('11月+24日の', [7.0, 8.6]), ('発売の', [10.3]), ('クラシックと', [11.7])],
    [('おでかけの', [13.4]), ('チケット', [14.9]), ('言うわね', [16.1])],
    [('朝 10時', [19.1, 19.8]), ('下野竜也と', [20.5]), ('高橋英樹 東京', [22.4, 24.5])],
    [('宮田大と', [25.7]), ('辻本玲の チェロ', [27.1, 29.0]), ('東京', [29.9])],
    [('川平慈英', [32.5]), ('伊原剛志', [34.2]), ('彩乃かなみ 山口', [35.8, 37.5])],
    [('タサン志麻 大阪', [38.6, 40.0])],
    [('珠光茶会 奈良', [40.9, 42.4]), ('先行', [43.2])],
    [('11時', [47.1]), ('野村萬斎たち', [48.2]), ('東京 先行', [51.3, 51.8])],
    [('夜 7時', [52.7, 53.7]), ('新国立劇場', [54.8]), ('オペラ 東京 先行', [57.1, 57.7, 58.4])],
    [('ほかにも あるわ', [59.3, 62.2]), ('見逃さないでね', [63.3])],
    [('売り場まで', [68.6]), ('案内+するのは', [71.0, 71.5]), ('おしなび', [72.7])],
    [('公演と', [74.7]), ('アーティストの', [76.2]), ('紹介も 載せてるわ', [77.8, 79.0])],
    [('oshinavi+.jp', [83.0, 86.3]), ('なのよ', [87.4])],   # すちこ 11/13「検索するのは小文字だから小文字で表示して」
]
LOW = {10, 11}
DUR = 97.34
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

CHORUS_AT, URL_AT = chunks[10]['show'], chunks[12]['show']   # 11/14 「公演とアーティストの紹介も載せてるわ／売り場まで案内するのは おしなび」＝タップの場面・「OSHINAVI.jp なのよ」から締め
chunks[12]['cy'] = 1080   # 11/13 締め「OSHINAVI.jp／だわ」は少し上＝下の段の4人（1260〜1490）の頭に重ねない
# 前奏（0〜4.1 秒）も真ん中を空けない＝「明日 11/10(火)／発売の お笑い」を白で出しておく（なぞらない）
if chunks[0]['show'] > 1.0:   # 11/11 歌い出し 0.5 秒＝前奏の塊は要らない（最初の塊が 0.17 秒から出ている）
    chunks.insert(0, {'show': 0.3, 'hide': chunks[0]['show'], 'lines': [[['クラシックと', 999, False]], [['おでかけ', 999, False]], [['11/24(火)', 999, True], ['発売', 999, False]]], 'low': False})
SHOTS = {'badge': {'img': D + 'cards/screen_badge.png', 'crop': [0, 0, 1080, 1920], 'boxes': [], 'title': '発売日のバッジをタップ', 'tap': True}}
SCENES = [[0.0, 'shot:dj_title'], [CHORUS_AT, 'shot:badge'], [URL_AT, 'shot:dj_url'], [DUR, 'shot:dj_url']]
karaoke = [{'start': c['show'], 'end': c['hide'], 'lines': [''.join(w + (' ' if s else '') for w, _, s in r) for r in c['lines']], 'times': []} for c in chunks]
S = {'when': '11/24(火) 発売', 'kind': 'クラシック',   # 「クラシック・おでかけ」は下の札の幅に入らず両端が切れた（11/20 絵コンテ） 'name': 'N響大河ドラマ&名曲コンサート',
     'out': D + 'out.mp4', 'song': D + 'song.mp3', 'posedir': D + 'poses',
     'dur': DUR, 'beat': 60 / B['bpm'], 'calm': True, 'fade_in': 0.0, 'fade_out': 1.5,
     'scenes': SCENES, 'karaoke': karaoke, 'chunks': chunks, 'panels': [[0.0, 1]], 'poses': [[0.0, 'r1']], 'blocks': {}, 'shots': SHOTS,
     'kara_size': 96, 'kara_y': 1000, 'kara_w': 960, 'kara_maxl': 5,
     'kara_col': {'done': [255, 228, 0], 'todo': [255, 255, 255], 'stroke': [20, 10, 40]},
     'shot_w': 600, 'shot_top': 250}
io.open(D + 'music_1123.json', 'w', encoding='utf-8').write(json.dumps(S, ensure_ascii=False, indent=1))
print('PH', PH, 'bar', round(bar, 3))
print('chunks', [(c['show'], c['hide']) for c in chunks])
