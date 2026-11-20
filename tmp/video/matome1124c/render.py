# -*- coding: utf-8 -*-
# 10/28 お笑いまとめ動画の書き出し（matome1027o/render.py の写し）
#   背景＝電球のドットの動画（bg_video・ループ・暗くぼかす）／キャラ＝パステル学園アイドルの切り抜き（立ち姿の6コマ）を拍で動かす／歌詞＝塊の入れ替え（白／黄）
#   タップの場面（サビ）＝本物のOSHINAVI（39688 囲碁将棋／ミキ）。out.mp4 → X 用 out_x.mp4（8.5MB 狙い）
#   引数 --frames 1.0,5.0,… なら書き出さずにその秒のコマだけ PNG で出す（frames/h_*.png）
import io, json, os, re, runpy, subprocess, sys
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
subprocess.run([sys.executable, D + 'make_spec.py'], check=True)
S = json.load(io.open(D + 'music_1123.json', encoding='utf-8'))
# 11/9 お笑いまとめ（紫髪の雨の子・雨粒の背景・タップは 41576 マルコポロリ）
# 11/9 紫髪の雨の子 9 ポーズ（r＝シートの向き・n＝反転）。タップの場面まで 8 着を1回ずつ・立つ／座るを交互
#   r1（百合の子）と r9（よく似た立ち姿）は 3 番目と 7 番目に離す。締めはいちばんかわいい1着＝桃色の和傘の子 r6
#   お辞儀の絵はシートに無い＝お辞儀の決まりは当てない（頭も締めも拍で動かす）
# 11/10 50年代レトロの子 9 ポーズ：r1 水玉で立つ／r2 赤いドレスとマイク／r3 ピンクの車にもたれる／r4 ダイナーの席（黒）／r5 ギンガムで跳ねる
#   ／r6 コートで歩く／r7 寝そべってレコード／r8 チアで膝立ち／r9 ダイナーの席（紅茶）。似た組＝r4 と r9（どちらもダイナーの席）は 2 番目と 6 番目に離す
#   立つ／座る／寝る／跳ぶを交互に。締めはいちばんかわいい1着＝両手を広げて跳ねるギンガムの子 r5
# 11/13 ニューヨーク・ちびガールズ（r＝シートの向き・n＝反転）：r1 帽子でしゃがむ／r2 I♥NY の袋で座る／r3 コーヒーで歩く／r4 スケボーで座る
#   ／r5 革ジャンで座る／r6 黒い帽子で腰かける／r7 緑の髪（腕3本＝使わない）／r8 投げキッス（締め）／r9 NYC のニット帽で座る
#   タップまで約 81 秒＝1人 8 秒以内には 11 人要る＝8着のうち締めの r8 以外の7着を1回ずつ → 反転で4着をもう一度（すぐ後ろ・となりに同じ服を置かない）
# 11/13 第2版（すちこ「立ってる画像をメインに・颯爽と歩くところを続けて」）＝歩く子 w（右向き）／m（反転＝左向き）
#   w1 キャップ／w2 赤い髪の毛皮コート／w3 青い髪のトレンチ／w4 紫の髪の革ジャン／w5 ピンクの髪の I♥NY 袋（締め）／w6 緑の髪のデニムとコーヒー
#   ／w7 NYC ニット帽／w8 ピンクの髪のスーツケース／w9 黒い帽子のトレンチ
# 11/11 パリコレの子（w/m＝歩く子・s/t＝座る子・m/t は反転）：歩く子3着（1 金髪のコート・3 青い髪のトレンチ・7 紙袋）は2回ずつ（2回目は反転＝左向き）
# 11/12 冬雪の子（全員歩く子・w＝右向き／m＝反転＝左向き）：9着を1回ずつ・向きを交互に・締めはピンクのダウンとハートのヘッドホンの子 w7
# 11/15 グルメの子（全員歩く子）：1枚目 w（右向き）/m（反転）・2枚目 a（右向き）/b（反転）＝2枚を交互に・向きも交互に
#   似た組（ケーキ w1/b1・すし w2/b2・コーヒー w6/b6・BBQ w7/a9）は離す。2枚目のビール c7 は使わない。締めはひまわり帽のアイスの子 w8
# 11/14 ちびファンタジーの子（同じピンク髪の子の衣装違い・2枚とも混ぜる）：1枚目 w（右向き）/m（反転）＝w1 紫の魔女／w2 天使（締め）／w3 悪魔
#   ／w4 エルフの弓／w5 青い騎士／s6 人魚（座る子＝まん中にふわっと）／w7 妖精／w8 赤い踊り子／w9 九尾（狐）
#   2枚目 a（右向き）/b（反転）＝a1 羽根帽の剣士／a2 氷の女王／a3 炎の魔女／a4 吸血鬼（ワイン）／a5 森の鹿の子／a6 スチームパンク／a7 薬の魔女／a8 海賊／a9 九尾（ちょうちん）
#   1枚目と2枚目を交互・向きも交互。似た組（九尾 w9/a9・魔女 w1/a3/a7・こうもりの羽 w3/a4・エルフ w4/a5・剣 w5/a1）はとなりに置かない＝九尾は b9 の1回だけ
#   タップまで約 47.5 秒＝10着を 1人 約 4.8 秒。締めはいちばん華やかな天使 w2
ORDER = ['s6', 't4', 's2', 't5', 's9', 't8', 's3', 't7', 's6', 't9', 's4', 's1']   # 11/24 クラシックとおでかけ（普段着の清楚な姐さん・すちこ 11/20）：1 白いブラウスとベージュのスカート（締めのまん中）／2 水色のニットのワンピース／3 キャメルのコートとマフラー／4 紺のカーディガンと白いプリーツ／5 グレーのタートルネックとパンツ／6 小花柄のワンピースにベレー帽（カバー）／7 白いシャツとデニムのスカートにトート／8 ピンクのニットとグレーのスカート／9 カーキのトレンチ（似た組＝コートの 3 と 9 はとなりに置かない）
_B = json.load(io.open(D + 'beats.json'))['beats']
_tap = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:badge')
_url = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:dj_url')
# 1人 8 秒以内：タップまで（約 62.4 秒＝136 拍）を 17 拍（7.8 秒）ずつ 8 着で割る・替えるのは拍の頭
LINE_AT = [0.0, 7.0, 13.4, 19.1, 25.7, 32.5, 38.6, 47.1, 52.7, 59.3, 63.3]   # 歌の行・言葉の頭（lyrics_times_head/2）＝1人 8 秒前後
_at = [0.0] + [max(b for b in _B if b <= s + 0.05) for s in LINE_AT[1:]]   # その直前の拍の頭
_N = len(ORDER) - 1
S['poses'] = [[t, ORDER[i]] for i, t in enumerate(_at)] + [[_url, ORDER[_N]]]
_len = [round((_at[i + 1] if i + 1 < _N else _tap) - _at[i], 2) for i in range(_N)]
print('出番の長さ', _len)
# 8 秒を超える出番（字のある服＝反転しない）は 8 秒目から少し大きく弾む
S['hop'] = [[_at[i] + 8.0, (_at[i + 1] if i + 1 < _N else _tap)] for i in range(_N) if _len[i] > 8.0]
print('弾む', S['hop'])
print('poses', S['poses'])
S.update({'out': D + 'out.mp4', 'posedir': D + 'poses', 'char_scale': 1.0, 'char_pos': [540, 870]})   # 11/1：1.3 倍の重ねがけを外す（大きさは beat_char の SCALE だけ）
S.pop('panels')
io.open(D + 'music_1123_v.json', 'w', encoding='utf-8').write(json.dumps(S, ensure_ascii=False, indent=1))
FR = None
CL = None
if '--clip' in sys.argv:
    CL = [float(x) for x in sys.argv[sys.argv.index('--clip') + 1].split(',')]
if '--frames' in sys.argv:
    FR = [float(x) for x in sys.argv[sys.argv.index('--frames') + 1].split(',')]
sys.path.insert(0, 'tools')
sys.path.insert(0, D)
import oshimade_mv as M
import bg_video  # noqa: F401
import beat_char  # noqa: F401
import walk_char
walk_char.install(S)
sys.argv = ['shuyaku_video.py', D + 'music_1123_v.json']
g = runpy.run_path('tools/shuyaku_video.py', run_name='__main__')
import badge_tap
badge_tap.install(g['render'])
import dj_text
dj_text.install(g['render'])
import kara_style
kara_style.install(g['render'], S)
# 11/4 すちこ「最後の伴奏のところがまた真ん中が開いてる　だんだん上からキャラが下りてくるように」＝歌い終わり（最後の塊が消える 78.3 秒）から、
#   ほかの8着が1小節に1人ずつ上から落ちてきて、まん中に2段（4人ずつ）で並ぶ＝締めは9人そろう
sys.path.insert(0, 'tmp/video')
import outro_parade
# 11/9 すちこ（11/8）「せめて真ん中埋まるくらい下ろしてきて」＝後奏（歌い終わり 78 秒〜93.6 秒・約 15 秒）に 8 人を1小節に1人ずつ下ろし、
#   まん中に2段（上 880〜1180・下 1180〜1480）×4人で並べる＝締めの r6 と合わせて9人そろう。9着とも前半に出ている＝向きを反転（n）して出す
#   並ぶ位置：百合の子 n1 と似た立ち姿 n9 は上の段の左端と下の段の右端に離す。座る子と立つ子が上下・左右で交互になるように
# 11/10：この曲は後奏がほとんど無い（歌い終わり 57.0 秒・曲の終わり 58.8 秒）＝締めの場面（OSHINAVI.jp／なのよ・53.8 秒〜）に入った所から
#   1拍に1人ずつ 4 人を下ろし、歌詞の塊（1000〜1240）の下・oshinavi.jp の文字（1500〜）の上の段（1260〜1490）に並べる
#   ＝上の締めの r5 と合わせて 5 人。9 着とも前半に出ている＝向きを反転（n）して出す。ダイナーの席の n4 と n9 はとなりに置かない
_R = [(135 + 270 * i, 1490, 230) for i in range(4)]
PARADE = [('s5', _R[0]), ('s2', _R[1]), ('s4', _R[2]), ('s9', _R[3])]   # 11/24 下の段＝グレーのタートル・水色のニット・紺のカーディガン・カーキのトレンチ（まん中の白いブラウス s1 と重ねない）
for j, (nm, (cx, bt, hh)) in enumerate(PARADE):   # 横に広い子（窓・ベンチ・階段）が画面の端で切れない＝内側へ寄せる
    ww = outro_parade.pose(S['posedir'], nm, hh).width
    PARADE[j] = (nm, (max(ww / 2 + 6, min(1080 - ww / 2 - 6, cx)), bt, hh))
outro_parade.install(g['render'], S, [{'t0': _url + S['beat'] * 2, 't1': S['dur'] + 1, 'step': S['beat'] * 2, 'names': [n for n, _ in PARADE], 'slots': [s for _, s in PARADE]}])
print('締めの段', _url, '〜', S['dur'], [n for n, _ in PARADE])
G = g['render'].__globals__
# 11/16 TikTok のカバー（すちこ 11/15）＝頭の 1.0 秒は、字（クラシック／11/19(木) 発売）と子がそろった 1.0 秒後のコマで止める
_orig_render = G['render']


def _cover_render(t, S2):
    if t < 1.0:
        return _orig_render(1.0, S2)
    return _orig_render(t, S2)


G['render'] = _cover_render
if FR:
    os.makedirs(D + 'frames', exist_ok=True)
    for t in FR:
        G['render'](t, S).save(D + 'frames/h_%05.1f.png' % t)
        print('frame', t, M.CUR.get('pose'))
    sys.exit(0)
if CL:                                   # 試し動画＝[A,B) の秒だけ書き出す（音はその区間）→ clip.mp4
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
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
src, dst = D + 'out.mp4', D + 'out_x.mp4'
info = subprocess.run([ff, '-i', src], capture_output=True, text=True, errors='replace').stderr
m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', info)
dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
vk = int((8.5 * 8 * 1024) / dur) - 128
subprocess.run([ff, '-y', '-v', 'error', '-i', src, '-c:v', 'libx264', '-b:v', f'{vk}k', '-maxrate', f'{vk}k', '-bufsize', f'{2 * vk}k',
                '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', dst], capture_output=True)
io.open(D + 'render.txt', 'w', encoding='utf-8').write('%s %.2fMB / %s %.2fMB dur=%.2f v=%dk\n' % (src, os.path.getsize(src) / 1048576, dst, os.path.getsize(dst) / 1048576, dur, vk))
print('done', dst)
