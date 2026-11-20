# -*- coding: utf-8 -*-
# 11/11 お笑い（X 今夜・1:15.7・95.6BPM）：パリコレの子の名前づけ・walk_char（歩く子は歩いて入る／座る子はその場でふわっと）・make_spec の塊・render の並び
#   歩く子＝cp1 金髪のチェックのコートとコーヒー・cp3 青い髪のトレンチと帽子・cp7 水色の髪の紙袋 → w（右向き）／m（反転＝左向き）
#   座る子＝cp2 赤いドレスでカフェ・cp4 紫の髪でシャンパン・cp5 ピンクの髪でエッフェル塔（締め）・cp6 銀髪のめがねで読書・cp8 黒い帽子でお茶・cp9 ピンクの髪で猫 → s（右向き）／t（反転）
import io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
from PIL import Image, ImageOps
for f in os.listdir(D + 'poses'):
    if re.fullmatch(r'[wmst]\d\.png', f):
        os.remove(D + 'poses/' + f)
for k in range(1, 10):
    im = Image.open(D + 'poses/cp%d.png' % k)
    a, b = ('w', 'm') if k in (1, 3, 7) else ('s', 't')
    im.save(D + 'poses/%s%d.png' % (a, k))
    ImageOps.mirror(im).save(D + 'poses/%s%d.png' % (b, k))

# ---- walk_char：座る子（s/t）は歩かせない＝まん中にその場で現れて（0.4 秒で上から少し下りながら濃くなる）、替わる時は 0.4 秒で薄くなって消える
wc = io.open(D + 'walk_char.py', encoding='utf-8').read()
wc = wc.replace("glob.glob(D + 'poses/[wm][1-9].png')", "glob.glob(D + 'poses/[wmst][1-9].png')")
wc = wc.replace("""def face(name):
    return 1 if name.startswith('w') else -1
""", """def face(name):
    return 1 if name[0] in 'ws' else -1


def walker(name):
    return name[0] in 'wm'
""")
wc = wc.replace("""def draw(im, name, xc, t):
    c = img(name)""", """def draw(im, name, xc, t, alpha=1.0, dy=0.0):
    c = img(name)""")
wc = wc.replace("""    c2 = c.rotate(ang, resample=Image.BICUBIC, expand=True)
    x = int(xc - c2.width / 2)
    y = int(BOT - c.height - (c2.height - c.height) / 2 + lift)
    im.paste(c2, (x, y), c2)""", """    c2 = c.rotate(ang, resample=Image.BICUBIC, expand=True)
    if alpha < 1.0:
        c2 = c2.copy()
        c2.putalpha(c2.getchannel('A').point(lambda v: int(v * max(0.0, alpha))))
    x = int(xc - c2.width / 2)
    y = int(BOT - c.height - (c2.height - c.height) / 2 + lift + dy)
    im.paste(c2, (x, y), c2)""")
wc = wc.replace("""        tin = t0 + (DELAY if k and face(P[k - 1][1]) != f else 0.0)
        if t < tin or (t1 is not None and t > t1 + EXB):
            continue""", """        if not walker(name):   # 座る子＝まん中にふわっと現れ、替わる時はふわっと消える
            FI = 0.4
            tin = t0 + (0.5 if k and walker(P[k - 1][1]) else 0.0)
            if t < tin or (t1 is not None and t > t1 + 0.15):
                continue
            a = min(1.0, (t - tin) / FI)
            if t1 is not None and t > t1 - 0.25:
                a = min(a, (t1 + 0.15 - t) / 0.4)
            draw(im, name, W / 2, t, alpha=a, dy=-40 * (1 - min(1.0, (t - tin) / FI)) ** 2)
            continue
        tin = t0 + (DELAY if k and walker(P[k - 1][1]) and face(P[k - 1][1]) != f else 0.0)
        if t < tin or (t1 is not None and t > t1 + EXB):
            continue""")
for need in ("def walker(name)", "alpha=a, dy=", "[wmst][1-9]", "c2.putalpha("):
    assert need in wc, need
io.open(D + 'walk_char.py', 'w', encoding='utf-8').write(wc)

# ---- make_spec：歌詞の塊（時刻＝lyrics_times2.txt の言葉の頭・文言＝USLT と一致の mine.txt・名前はサイトの表記）
ms = io.open(D + 'make_spec.py', encoding='utf-8').read()
a, b = ms.index('CHUNKS = ['), ms.index('LOW = {12, 13}')
ms = ms[:a] + """CHUNKS = [
    [('明日 11月+11日の', [0.5, 1.6, 2.8]), ('発売の お笑い', [4.8, 6.6]), ('言うわよ', [7.7])],
    [('午前 10時は', [10.0, 10.8]), ('とろサーモン 東京', [11.4, 12.4])],
    [('NON STYLE', [14.7, 15.8]), ('石田明 大阪', [16.2, 17.4]), ('NMB+48 大阪', [19.4, 20.7, 22.6])],
    [('3時のヒロイン', [24.8]), ('ゆめっち 東京', [26.1, 26.8]), ('ダンビラムーチョ', [27.7]), ('蛙亭 東京', [28.8, 29.4])],
    [('月亭+方正 大阪', [30.2, 30.8, 32.1]), ('立川+談笑 東京', [34.8, 35.5, 36.0]), ('忘れないでね', [37.3])],
    [('午前 11時は', [40.1, 40.8]), ('桂+南光 愛知', [42.0, 42.7, 43.2]), ('先行', [43.8])],
    [('昼 12時は', [45.3, 45.8]), ('神田+伯山 東京', [47.1, 47.7, 48.3]), ('新開地 喜楽館', [50.2, 51.1]), ('兵庫', [52.5])],
    [('夜 10時+45分は', [53.1, 53.3, 53.8]), ('おしゃべり達の 集い', [55.3, 56.8]), ('東京', [57.7])],
    [('笑いに 行くのが', [60.5, 61.4]), ('楽しみだわ', [62.0])],
    [('売り場まで', [64.3]), ('案内+するのは', [66.3, 67.3]), ('おしなび', [68.4])],
    [('OSHINAVI+.jp', [69.7, 71.8]), ('なのよ', [73.1])],
]
""" + ms[b:]
ms = ms.replace('LOW = {12, 13}', 'LOW = {9}').replace('DUR = 107.0', 'DUR = 75.7')
ms = ms.replace("CHORUS_AT, URL_AT = chunks[12]['show'], chunks[14]['show']", "CHORUS_AT, URL_AT = chunks[9]['show'], chunks[10]['show']")
ms = ms.replace("chunks[14]['cy'] = 1080", "chunks[10]['cy'] = 1080")
ms = ms.replace("'lines': [[['11/13(金)', 999, False]], [['発売の', 999, True], ['お笑い', 999, False]]]",
                "'lines': [[['11/11(水)', 999, False]], [['発売の', 999, True], ['お笑い', 999, False]]]")
ms = ms.replace("S = {'when': '11/13(金) 発売', 'kind': 'お笑い', 'name': 'とろサーモン久保田 初ソロトークライブ',",
                "S = {'when': '明日 11/11(水) 発売', 'kind': 'お笑い', 'name': 'SUN「新春！よしもと大爆笑2027」',")
for need in ("LOW = {9}", "DUR = 75.7", "chunks[9]['show']", "chunks[10]['cy']", "'11/11(水)'", "新春！よしもと大爆笑2027"):
    assert need in ms, need
io.open(D + 'make_spec.py', 'w', encoding='utf-8').write(ms)

# ---- render：タップまで（約 63.5 秒）を 9 人で割る（1人 8 秒以内）＝歩く子と座る子を交互・歩く子を多めに（反転でもう一度）
#   締め＝エッフェル塔の子 s5／後奏（約 6 秒）＝2拍に1人ずつ4人（猫の子 s9・紙袋の子 m7・シャンパンの子 t4・トレンチの子 w3）
rd = io.open(D + 'render.py', encoding='utf-8').read()
rd = re.sub(r"ORDER = \['w1', 'w2'.*?\]\n", """# 11/11 パリコレの子（w/m＝歩く子・s/t＝座る子・m/t は反転）：歩く子3着（1 金髪のコート・3 青い髪のトレンチ・7 紙袋）は2回ずつ（2回目は反転＝左向き）
ORDER = ['w1', 's4', 'w3', 's6', 'w7', 's2', 'm1', 's8', 'm3', 's5']
""", rd, count=1, flags=re.S)
rd = rd.replace("PARADE = [('n2', _R[0]), ('n6', _R[1]), ('n5', _R[2]), ('r9', _R[3])]   # 11/13 後奏 約 18 秒＝1小節に1人ずつ4人（座る子を交互の向きで）",
                "PARADE = [('s9', _R[0]), ('m7', _R[1]), ('t4', _R[2]), ('w3', _R[3])]   # 11/11 後奏 約 6 秒＝2拍に1人ずつ4人")
rd = rd.replace("'step': S['beat'] * 4, 'names'", "'step': S['beat'] * 2, 'names'")
for need in ("ORDER = ['w1', 's4'", "('s9', _R[0])", "S['beat'] * 2"):
    assert need in rd, need
io.open(D + 'render.py', 'w', encoding='utf-8').write(rd)
print('ok')
