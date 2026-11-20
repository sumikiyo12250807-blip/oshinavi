# -*- coding: utf-8 -*-
# 11/20 J-POP（1:48）：matome1119c から写した make_spec・render・shoot_badge・kara_style を 11/20 用に差し替える
#   すちこ「JPOPはファッションをゴスロリにして」＝ゴスロリの姐さん9人（全員 右向き＝s／反転 t）・歩かせない
#   背景 242696（すちこが渡した・黒×えんじのダイヤ柄・暗い）＝字は白／黄・縁は濃い色
#   時刻＝lyrics_times2.txt（言葉の頭）。名前はサイトの表記（index.html の登録・tmp/x1117/x/check_jpop_1120.py で突き合わせ済み）
import io, re, shutil, subprocess
import imageio_ffmpeg
from PIL import Image, ImageOps
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
P = D + 'poses/'
for k in range(1, 10):
    shutil.copyfile(P + 'w%d.png' % k, P + 's%d.png' % k)
    ImageOps.mirror(Image.open(P + 'w%d.png' % k)).save(P + 't%d.png' % k)
ff = imageio_ffmpeg.get_ffmpeg_exe()
e = subprocess.run([ff, '-i', D + 'song.mp3'], capture_output=True, text=True, errors='replace').stderr
m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', e)
DUR = round(int(m.group(2)) * 60 + float(m.group(3)), 2)
print('DUR', DUR)

# 拍（81BPM 前後＝tempo_check 80.8）
s = io.open(D + 'beats_1114.py', encoding='utf-8').read()
for a, b in (('END = 67.5', 'END = %.1f' % (DUR - 0.3)), ('np.arange(100.5, 101.51, 0.05)', 'np.arange(80.3, 81.31, 0.02)'),
             ('fit(SN, b, 1, 66, 0.002)', 'fit(SN, b, 1, %.1f, 0.002)' % (DUR - 1.5)), ('range(0, 70, 10)', 'range(0, 110, 10)'),
             ("beats_1114.txt", "beats_1120.txt")):
    assert a in s, a
    s = s.replace(a, b)
io.open(D + 'beats_1120.py', 'w', encoding='utf-8').write(s)
subprocess.run(['python', D + 'beats_1120.py'], check=True)

ms = io.open(D + 'make_spec.py', encoding='utf-8').read()
a, b = ms.index('CHUNKS = ['), ms.index('LOW = {')
ms = ms[:a] + """CHUNKS = [
    [('11月+20日', [11.8, 13.7]), ('金曜日の', [16.4]), ('発売の J-POPの', [17.6, 18.9]), ('チケット 言うわよ', [21.9, 24.4])],
    [('午前 10時は', [30.0, 30.5]), ('世良公則 東京', [31.3, 33.0])],
    [('早見優', [34.0]), ('松本伊代', [35.1]), ('森口博子', [36.2]), ('福岡 ほか', [37.6, 38.3])],
    [('中村雅俊', [38.7]), ('東京 ほか', [40.2, 41.5])],
    [('小椋佳 全国', [42.6, 43.5]), ('純烈 全国', [44.1, 45.0])],
    [('清水ミチコ 全国', [45.5, 46.4]), ('甘い暴力 東京', [47.1, 47.9])],
    [('午前 11時は', [48.7, 48.9]), ('イモ欽トリオ 東京', [50.2, 51.4])],
    [('お昼 12時は', [52.9, 53.4]), ('矢井田瞳 京都', [54.6, 56.7])],
    [('北山修 東京', [57.4, 59.3])],
    [('安部恭弘 千葉 ほか', [60.6, 62.0, 62.3])],
    [('懐かしい 歌が', [63.1, 64.2]), ('いっぱいね', [64.6])],
    [('ほかにも あるわ', [65.7, 67.2]), ('忘れないでね', [67.6])],
    [('あの頃の 歌を', [69.6, 70.8]), ('生で 聴きたいわ', [71.8, 72.3])],
    [('oshinavi+.jpで', [73.0, 73.9]), ('名前を', [75.0]), ('検索してね', [75.8])],
    [('公演と', [77.1]), ('アーティストの', [78.0]), ('紹介も 載せてるわ', [78.7, 79.3])],
    [('売り場まで', [81.3]), ('案内+するのは', [82.6, 83.2]), ('おしなび', [84.2])],
    [('Xの フォローも', [85.1, 85.8]), ('しておいて', [86.5])],
    [('毎日 情報', [87.3, 88.3]), ('発信しているの', [89.2])],
    [('oshinavi+.jp', [90.8, 91.4]), ('なのよね', [92.5])],   # すちこ 11/13「検索するのは小文字だから小文字で表示して」
]
""" + ms[b:]
pairs = [('LOW = {12, 13}', 'LOW = {14, 15}'), ('DUR = 96.02', 'DUR = %.2f' % DUR),
         ("CHORUS_AT, URL_AT = chunks[12]['show'], chunks[14]['show']", "CHORUS_AT, URL_AT = chunks[14]['show'], chunks[18]['show']"),
         ("chunks[14]['cy'] = 1080", "chunks[18]['cy'] = 1080"),
         ("'lines': [[['クラシック', 999, False]], [['11/19(木)', 999, True], ['発売', 999, False]]]",
          "'lines': [[['J-POP', 999, False]], [['11/20(金)', 999, True], ['発売', 999, False]]]"),
         ("S = {'when': '11/19(木) 発売', 'kind': 'クラシック', 'name': 'みなとみらい',",
          "S = {'when': '11/20(金) 発売', 'kind': 'J-POP', 'name': '世良公則',"),
         ("'classic_1119.json'", "'jpop_1120.json'")]
for x, y in pairs:
    if x not in ms:
        print('!! make_spec に無い:', x)
        continue
    ms = ms.replace(x, y)
body = ms.split('CHUNKS = [')[1].split('karaoke = [')[0]
for bad in ('みなとみらい', 'クラシック', '11/19', 'センチュリー'):
    assert bad not in body, bad
io.open(D + 'make_spec.py', 'w', encoding='utf-8').write(ms)

r = io.open(D + 'render.py', encoding='utf-8').read()
r = r.replace("'classic_1119.json'", "'jpop_1120.json'").replace("'classic_1119_v.json'", "'jpop_1120_v.json'")
a = r.index('ORDER = ['); b = r.index('\n', a)
r = r[:a] + ("ORDER = ['s1', 't3', 's5', 't2', 's8', 't5', 's4', 't1', 's6', 't9', 's9', 't4', 's7', 't6', 's2', 't7', 's3', 't8']   # 11/20 J-POP（ゴスロリの姐さん・歩かせない）："
             "前奏＝黒白ボンネット s1→紫 t3／「11月20日」＝マイク s5／発売のJ-POP＝赤い王冠 t2／言うわよ＝白い王冠 s8／世良公則＝マイク t5"
             "／早見優・松本伊代・森口博子＝白ロリうさぎ s4／中村雅俊＝黒白 t1／小椋佳・純烈＝パラソル s6／清水ミチコ・甘い暴力＝赤黒の帽子 t9"
             "／イモ欽トリオ＝帽子 s9／矢井田瞳＝うさぎ t4／北山修＝本 s7／安部恭弘＝パラソル t6／懐かしい歌＝赤い王冠 s2／ほかにも＝本 t7"
             "／あの頃の歌を＝紫 s3／検索＝白い王冠 t8") + r[b:]
a = r.index('LINE_AT = ['); b = r.index('\n', a)
r = r[:a] + "LINE_AT = [0.0, 6.0, 11.8, 17.6, 24.7, 30.0, 34.0, 38.7, 42.6, 45.5, 48.7, 52.9, 57.4, 60.6, 63.1, 65.7, 69.6, 73.0]   # 歌の行・言葉の頭（lyrics_times2.txt）＝1人 8 秒以内" + r[b:]
a = r.index('PARADE = ['); b = r.index('\n', a)
r = r[:a] + "PARADE = [('s5', _R[0]), ('s4', _R[1]), ('t2', _R[2]), ('t1', _R[3])]   # 11/20 下の段＝マイク・うさぎ・赤ツインテール・紅茶（まん中の王冠 t8 と重ねない）" + r[b:]
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)

sb = io.open(D + 'shoot_badge.py', encoding='utf-8').read()
x = "CID, Q, MD = 49293, 'みなとみらい', '11/19'"
sb = sb.replace(x, "CID, Q, MD = 26834, '世良公則', '11/20'")
y = 'new D(2026,10,16,20,0)'
sb = sb.replace(y, 'new D(2026,10,17,20,0)')
assert "26834, '世良公則'" in sb and 'new D(2026,10,17,20,0)' in sb   # TikTok 先出し＝11/17 の夜に撮る
io.open(D + 'shoot_badge.py', 'w', encoding='utf-8').write(sb)

ks = io.open(D + 'kara_style.py', encoding='utf-8').read()
x = "        else:     # 11/19 背景 49445 は明るい青いタイル＝字を暗く：まだ＝濃紺／歌った＝えんじ・縁は白の太め＋うっすら影（11/16 主役と同じ）\n            todo, done, stroke, shadow = NAVY, ENJI, WHITE, (0, 0, 0, 70)"
x = "        else:     # 11/19 背景 221717（黒地に赤と青の光の板・暗い）＝白／黄・縁は濃紺（暗い背景のいつもの形・11/18 舞台 21865 と同じ）\n            todo, done, stroke, shadow = WHITE, YEL, (20, 10, 40), (0, 0, 0, 150)"
ks = ks.replace(x, "        else:     # 11/20 背景 242696 は黒×えんじのダイヤ柄（暗い）＝白／黄・縁は濃紺（11/17 J-POP と同じ）\n            todo, done, stroke, shadow = WHITE, YEL, (20, 10, 40), (0, 0, 0, 150)")
io.open(D + 'kara_style.py', 'w', encoding='utf-8').write(ks)
print('ok')
