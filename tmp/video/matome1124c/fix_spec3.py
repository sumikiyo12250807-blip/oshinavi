# -*- coding: utf-8 -*-
# 10/31(土)発売 お笑いまとめ（Suno『おしなびどっと (5)』1:36.4・ドレスのマツコ9着・夜空と雲の動画 40242）に差し替え
#   make_spec：歌詞の塊（時刻＝lyrics_times2.txt の faster-whisper（歌詞を手がかり）・綴り＝曲の USLT＝渡した歌詞と全行一致・表記は owarai_material.txt）
#   shoot_badge：タップの場面のカード＝31804 さらば青春の光寄席（10/31 11:00 発売）・前の夜の時計 10/30 20:00
#   render.py：bg_video3（ペンライトの上の黒を埋める）は使わない・衣装の順と替える時刻・--clip（試し動画だけ書き出す）
#   bg_video.py：このフォルダの bgf（29.97fps・15.02秒）
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'


def sub(p, R):
    s = io.open(D + p, encoding='utf-8').read()
    for x, y in R:
        assert s.count(x) == 1, (p, x)
        s = s.replace(x, y)
    io.open(D + p, 'w', encoding='utf-8').write(s)


p = D + 'make_spec.py'
s = io.open(p, encoding='utf-8').read()
a = s.index('CHUNKS = [')
b = s.index(']\nLOW') + 2
NEW = '''CHUNKS = [
    [('明日 10/31の', [11.0, 12.1]), ('発売の', [14.4]), ('お笑い 言うわよ', [15.6, 16.0])],
    [('9時', [16.9]), ('どぶろっく 真空ジェシカ', [17.6, 18.6]), ('神奈川', [20.0])],
    [('10時', [21.5]), ('M-1+グランプリ 3回戦', [22.6, 23.3, 24.2]), ('東京', [25.4])],
    [('もう中学生 東京', [27.0, 29.5]), ('トータルテンボス COWCOW', [31.9, 33.3]), ('東京', [34.0])],
    [('工藤遥 ラブレターズ 東京', [34.9, 35.6, 36.7]), ('春風亭+一之輔 熊本 ほか', [37.5, 38.8, 39.6, 40.6])],
    [('モグライダー 東京', [40.9, 41.9]), ('11時', [42.9]), ('さらば+青春の+光 東京', [43.8, 44.5, 45.7, 46.4])],
    [('バッテリィズ 銀シャリ 三重', [48.5, 49.9, 50.5]), ('ジェラードン 蛙亭 東京', [51.2, 52.3, 53.1])],
    [('バイク川崎バイク 東京', [54.5, 56.1]), ('カラタチ 例えば炎 千葉', [57.0, 57.8, 59.0])],
    [('12時', [59.5]), ('宮下草薙 東京', [60.2, 61.7]), ('NMB48 大阪', [63.8, 66.9])],
    [('ほかにも まだまだ', [68.9, 70.3]), ('あるのよ', [70.9])],
    [('売り場まで', [71.6]), ('案内するのは おしなび', [72.5, 74.0])],
    [('土曜日の 笑いも', [75.7, 79.3]), ('おしなびで', [81.0])],
    [('OSHINAVI+.jp だわ', [83.8, 86.3, 89.9])],
]
'''
s = s[:a] + NEW + s[b:]
io.open(p, 'w', encoding='utf-8').write(s)
sub('make_spec.py', [('LOW = {9, 10, 11, 12}', 'LOW = {10, 11}'),
                     ('DUR = 61.22', 'DUR = 96.0'),
                     ("CHORUS_AT, URL_AT = chunks[9]['show'], chunks[13]['show']", "CHORUS_AT, URL_AT = chunks[10]['show'], chunks[12]['show']"),
                     ("S = {'when': '明日 10/30(金) 発売', 'kind': 'お笑い', 'name': 'じゃるじぇらいす',",
                      "S = {'when': '明日 10/31(土) 発売', 'kind': 'お笑い', 'name': 'さらば青春の光寄席',")])
sub('shoot_badge.py', [("CID, Q, MD = 41568, 'じゃるじぇらいす', '10/30'", "CID, Q, MD = 31804, 'さらば青春の光', '10/31'"),
                       ('new D(2026,9,29,20,0)', 'new D(2026,9,30,20,0)')])
sub('bg_video.py', [("D = 'C:/Users/user/oshinavi/tmp/video/matome1024j/bgf/'", "D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/bgf/'"),
                    ('FPS, L, XF = 25.0, 30.02, 0.5', 'FPS, L, XF = 29.97, 15.02, 0.5')])
sub('render.py', [
    ('import bg_video3  # noqa: F401\n', ''),
    ("ORDER = ['p3', 'p4', 'p1', 'p8', 'p6', 'p5', 'p7', 'p9', 'p2']   # 色が続かないように並べ、最後の oshinavi.jp はいちばんかわいいピンクのハート（p2）",
     "ORDER = ['p1', 'p8', 'p2', 'p4', 'p3', 'p7', 'p9', 'p5', 'p6']   # 紫の玉座で始め、色が続かないように。最後の oshinavi.jp は立ち姿で全身が見えるバラの赤（p6）"),
    ("_two = [x for x in _bars[::2] if x < _tap - 1.0]          # 2小節ごと（約4.9秒）\n_at = [0.0] + _two[1:8]",
     "_at = [0.0] + [min((x for x in _bars if 0 < x < _tap - 2), key=lambda x: abs(x - _tap * k / 7)) for k in range(1, 7)]   # タップまでを7等分して小節の頭（約10秒・4小節ずつ）"),
    ("S['poses'] = [[t, ORDER[i]] for i, t in enumerate(_at[:7])] + [[_url, ORDER[7]], [_last, ORDER[8]]]",
     "S['poses'] = [[t, ORDER[i]] for i, t in enumerate(_at[:7])] + [[_url, ORDER[7]], [_last, ORDER[8]]]\n_url_bar = min(_bars, key=lambda x: abs(x - _url))"),
    ("FR = None\n", "FR = None\nCL = None\nif '--clip' in sys.argv:\n    CL = [float(x) for x in sys.argv[sys.argv.index('--clip') + 1].split(',')]\n"),
    ("G['render_all'](S)\n", """if CL:                                   # 試し動画＝[A,B) の秒だけ書き出す（音はその区間）→ clip.mp4
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    FPS = G['FPS']
    A, Bv = CL
    p = subprocess.Popen([ff, '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (M.W, M.H), '-r', str(FPS), '-i', '-',
                          '-ss', str(A), '-t', str(Bv - A), '-i', S['song'], '-af', 'afade=t=in:st=0:d=0.3,afade=t=out:st=%.2f:d=0.5' % (Bv - A - 0.5),
                          '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '23', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', '-shortest',
                          D + 'clip.mp4'], stdin=subprocess.PIPE)
    n = int(round((Bv - A) * FPS))
    for i in range(n):
        p.stdin.write(G['render'](A + i / FPS, S).convert('RGB').tobytes())
    p.stdin.close(); p.wait()
    print('clip', A, Bv, os.path.getsize(D + 'clip.mp4') // 1024, 'KB')
    sys.exit(0)
G['render_all'](S)
"""),
])
io.open(D + 'fix_spec3.txt', 'w').write('ok')
print('ok')
