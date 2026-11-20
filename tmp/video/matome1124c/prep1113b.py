# -*- coding: utf-8 -*-
# 11/13 お笑い（TikTok 用・1:47）：子（cn1〜9 → r1〜9・反転 n1〜9）・make_spec の歌詞の塊・render の並び → 絵コンテ → 試し動画2本
#   🚨 r7（緑の髪の子）は腕が3本＝使わない（すちこ）。8着＝r1,r2,r3,r4,r5,r6,r8,r9
import io, os, re, shutil, subprocess, sys, json
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1113b.txt', 'w', encoding='utf-8')
from PIL import Image, ImageOps
for k in range(1, 10):
    im = Image.open(D + 'poses/cn%d.png' % k)
    im.save(D + 'poses/r%d.png' % k)
    ImageOps.mirror(im).save(D + 'poses/n%d.png' % k)


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s %s rc %s\n%s\n%s\n' % (f, a, r.returncode, r.stdout[-3000:], r.stderr[-3000:]))
    out.flush()
    return r.returncode


# ---- make_spec：歌詞の塊（時刻＝lyrics_times2.txt の言葉の頭・文言＝USLT と一致の mine.txt・名前はサイトの表記）
ms = io.open(D + 'make_spec.py', encoding='utf-8').read()
a, b = ms.index('CHUNKS = ['), ms.index('LOW = {7}')
ms = ms[:a] + """CHUNKS = [
    [('11月13日 金曜日', [15.2, 17.9]), ('発売の お笑い', [18.6, 19.4]), ('言うわよ', [20.4])],
    [('ジャイアンツと コラボの', [21.7, 22.7]), ('ステージ', [23.1]), ('麒麟 川島', [23.4, 24.1]), ('ナイツ 塙', [24.5, 24.9])],
    [('ビビる大木', [25.4]), ('東京 11時', [26.9, 27.6]), ('先行よ', [28.3])],
    [('チョコレート', [30.0]), ('プラネット 松尾の', [30.9, 31.6]), ('大忘年会', [32.0]), ('ニューヨーク 嶋佐も', [32.9, 33.6])],
    [('東京 13時', [34.3, 34.7]), ('とろサーモン 久保田', [35.4, 36.0]), ('初めての ソロトーク', [36.3, 36.9]), ('東京 10時', [37.6, 38.1])],
    [('ヘンダーソン', [38.5]), ('中村フー', [39.8]), ('青木マッチョも', [40.2]), ('千葉 10時', [41.0, 41.5]), ('忘れないでね', [42.0])],
    [('春風亭一之輔', [45.3]), ('石川 10時', [47.4, 48.3]), ('佐久間一行', [49.0]), ('東京 10時', [51.1, 52.0])],
    [('立川志の春と', [52.7]), ('三山ひろし', [54.2]), ('東京 10時', [55.3, 55.9]), ('柳家喬太郎', [56.5]), ('東京 10時', [58.0, 58.6])],
    [('春風亭小朝', [60.1]), ('神奈川 10時', [62.3, 62.7]), ('アイドルの', [63.4]), ('NMB48の', [64.5]), ('劇場公演も', [66.4])],
    [('大阪 12時', [67.4, 67.9]), ('先行よ', [68.4]), ('長野', [69.5]), ('コントするだら', [69.8]), ('長野 12時', [70.6, 71.1])],
    [('ライオンロック', [71.8]), ('たちの 仁王立ち', [72.9, 73.0]), ('東京と 大阪', [73.8, 74.3]), ('夜から', [74.8]), ('楽しみだわ', [75.8])],
    [('先行の条件は', [77.5]), ('先に 確かめてね', [79.5, 79.8])],
    [('oshinavi.jpで', [81.0]), ('名前を 検索してね', [83.0, 83.5])],
    [('売り場まで', [84.9]), ('案内するのは', [86.9]), ('おしなび', [87.7])],
    [('OSHINAVI+.jp', [88.4, 89.2]), ('だわ', [90.0])],
]
""" + ms[b:]
ms = ms.replace('LOW = {7}', 'LOW = {12, 13}').replace('DUR = 58.8', 'DUR = 107.0')
ms = ms.replace("CHORUS_AT, URL_AT = chunks[7]['show'], chunks[8]['show']", "CHORUS_AT, URL_AT = chunks[12]['show'], chunks[14]['show']")
ms = ms.replace("'lines': [[['明日', 999, True], ['11/10(火)', 999, False]], [['発売の', 999, True], ['お笑い', 999, False]]]",
                "'lines': [[['11/13(金)', 999, False]], [['発売の', 999, True], ['お笑い', 999, False]]]")
ms = ms.replace("S = {'when': '明日 11/10(火) 発売', 'kind': 'お笑い', 'name': 'M-1グランプリ2026 準々決勝',",
                "S = {'when': '11/13(金) 発売', 'kind': 'お笑い', 'name': 'とろサーモン久保田 初ソロトークライブ',")
for need in ("LOW = {12, 13}", "DUR = 107.0", "chunks[12]['show']", "'11/13(金)'", "とろサーモン久保田"):
    assert need in ms, need
io.open(D + 'make_spec.py', 'w', encoding='utf-8').write(ms)

# ---- render：タップまで（約 81 秒）を 11 人で割る（1人 8 秒以内）・締めは r8（投げキッス）・後奏は1小節に1人ずつ4人
rd = io.open(D + 'render.py', encoding='utf-8').read()
rd = re.sub(r"ORDER = \[.*?\]\n", """# 11/13 ニューヨーク・ちびガールズ（r＝シートの向き・n＝反転）：r1 帽子でしゃがむ／r2 I♥NY の袋で座る／r3 コーヒーで歩く／r4 スケボーで座る
#   ／r5 革ジャンで座る／r6 黒い帽子で腰かける／r7 緑の髪（腕3本＝使わない）／r8 投げキッス（締め）／r9 NYC のニット帽で座る
#   タップまで約 81 秒＝1人 8 秒以内には 11 人要る＝8着のうち締めの r8 以外の7着を1回ずつ → 反転で4着をもう一度（すぐ後ろ・となりに同じ服を置かない）
ORDER = ['r1', 'r2', 'r3', 'r4', 'r9', 'r6', 'r5', 'n3', 'n4', 'n1', 'n9', 'r8']
""", rd, count=1, flags=re.S)
rd = rd.replace("_at = [0.0] + [min(_B, key=lambda b: abs(b - _tap * k / 8.0)) for k in range(1, 8)]   # 等分にいちばん近い拍の頭",
                "_N = len(ORDER) - 1\n_at = [0.0] + [min(_B, key=lambda b: abs(b - _tap * k / _N)) for k in range(1, _N)]   # 等分にいちばん近い拍の頭")
rd = rd.replace("S['poses'] = [[t, ORDER[i]] for i, t in enumerate(_at)] + [[_url, ORDER[8]]]", "S['poses'] = [[t, ORDER[i]] for i, t in enumerate(_at)] + [[_url, ORDER[_N]]]")
rd = rd.replace("_len = [round((_at[i + 1] if i + 1 < 8 else _tap) - _at[i], 2) for i in range(8)]", "_len = [round((_at[i + 1] if i + 1 < _N else _tap) - _at[i], 2) for i in range(_N)]")
rd = rd.replace("PARADE = [('n1', _R[0]), ('n4', _R[1]), ('n2', _R[2]), ('n8', _R[3])]",
                "PARADE = [('n2', _R[0]), ('n6', _R[1]), ('n5', _R[2]), ('r9', _R[3])]   # 11/13 後奏 約 18 秒＝1小節に1人ずつ4人（座る子を交互の向きで）")
rd = rd.replace("'step': S['beat'], 'names'", "'step': S['beat'] * 4, 'names'")
for need in ("_N = len(ORDER) - 1", "ORDER[_N]", "range(_N)", "('n2', _R[0])", "S['beat'] * 4"):
    assert need in rd, need
io.open(D + 'render.py', 'w', encoding='utf-8').write(rd)

if run('render.py', '--frames', '0.5') != 0:
    out.close(); sys.exit(1)
S = json.load(io.open(D + 'stage_1118_v.json', encoding='utf-8'))
out.write('poses %s\nchunks %s\n' % ([[round(t, 2), p] for t, p in S['poses']], [(round(c['show'], 2), round(c['hide'], 2)) for c in S['chunks']]))
P = S['poses']
tap = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:badge')
url = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:dj_url')
n = len(P) - 1
TS = [6.0]
for i in range(n):
    m = (P[i][0] + (P[i + 1][0] if i + 1 < n else tap)) / 2
    for c in S['chunks']:
        if abs(m - c['show']) < 0.4:
            m = c['show'] + 0.6
    TS.append(round(m, 1))
TS += [round(tap + 3.0, 1), round(url + 1.0, 1), round(url + 6.0, 1), round(url + 10.0, 1), round(S['dur'] - 2.0, 1)]
out.write('TS %s\n' % TS)
bd = io.open(D + 'board.py', encoding='utf-8').read()
bd, k = re.subn(r"TS = \[38\.0\] if '--one' in sys\.argv else \[.*?\]", "TS = [38.0] if '--one' in sys.argv else %s" % TS, bd, count=1)
assert k == 1
io.open(D + 'board.py', 'w', encoding='utf-8').write(bd)
run('board.py')
out.write(io.open(D + 'board.txt', encoding='utf-8').read())
run('render.py', '--clip', '44.6,58.9')
shutil.copyfile(D + 'clip.mp4', D + 'clip_names.mp4')
run('render.py', '--clip', '86.5,101.0')
shutil.copyfile(D + 'clip.mp4', D + 'clip_end.mp4')
out.close()
open(D + 'prep1113b.done', 'w').close()
