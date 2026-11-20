# -*- coding: utf-8 -*-
# すちこ 11/13「説明と相撲の時は画像をあわせたらよくない？　相撲の時は化粧まわしの姐さんとかプロレスもあるよね？」
#   ＝歌っている行と衣装を合わせる。行が歌われ始める時刻（lyrics_times2）の直前の拍の頭で替える
#   前奏（〜大相撲の行）＝ボクサー w7 ／大相撲 春巡業 富士宮＝相撲 w1 ／東京女子プロレス＝女子プロレス w4 ／スターダム 大阪＝女子プロレス 反転 m4
#   ／サガン鳥栖 対 横浜FC＝サッカー w2 ／小島和哉のファンミーティング＝野球 w5 ／クボタスピアーズ 対 ブルーレヴズ＝ラグビー 反転 m3
#   ／西川遥輝と松本剛のトークショー・杉谷拳士も＝ペンライトのファン w9（野球は同じ本で2回出さない）／ほかにもあるわ 忘れないでね＝バスケ w8
#   タップの場面は今のまま・締めはチア w6 がまん中・下に4人（サッカー・野球が左で右向き／ラグビー・相撲が右で左向き）
#   8 秒を超える出番（前奏のボクサー 11.7 秒・バスケ 14 秒）は服に字がある＝反転しない → 8 秒目から1小節ごとに少し大きく弾ませる（walk_char の HOP）
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
r = io.open(D + 'render.py', encoding='utf-8').read()
a = r.index('ORDER = ['); b = r.index('\n', a)
r = r[:a] + "ORDER = ['w7', 'w1', 'w4', 'm4', 'w2', 'w5', 'm3', 'w9', 'w8', 'w6']   # 11/16 歌う行と衣装を合わせる（set_order4.py）・締めはチア w6" + r[b:]
a = r.index('_i0 = next('); b = r.index("assert max(_len) <= 8.0, _len") + len("assert max(_len) <= 8.0, _len")
r = r[:a] + """LINE_AT = [0.0, 11.7, 14.9, 19.6, 21.4, 24.6, 31.9, 38.2, 45.1]   # 行が歌われ始める秒（lyrics_times2.txt）
_at = [0.0] + [max(b for b in _B if b <= s + 0.05) for s in LINE_AT[1:]]   # その直前の拍の頭
_N = len(ORDER) - 1
S['poses'] = [[t, ORDER[i]] for i, t in enumerate(_at)] + [[_url, ORDER[_N]]]
_len = [round((_at[i + 1] if i + 1 < _N else _tap) - _at[i], 2) for i in range(_N)]
print('出番の長さ', _len)
# 8 秒を超える出番（字のある服＝反転しない）は 8 秒目から少し大きく弾む
S['hop'] = [[_at[i] + 8.0, (_at[i + 1] if i + 1 < _N else _tap)] for i in range(_N) if _len[i] > 8.0]
print('弾む', S['hop'])""" + r[b:]
a = r.index('PARADE = ['); b = r.index('\n', a)
r = r[:a] + "PARADE = [('w2', _R[0]), ('w5', _R[1]), ('m3', _R[2]), ('m1', _R[3])]   # 11/16 左2人は右向き（サッカー・野球）・右2人は左向き（ラグビー・相撲）＝真ん中を向く" + r[b:]
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)

w = io.open(D + 'walk_char.py', encoding='utf-8').read()
if "_S['HOP']" not in w:
    w = w.replace("def install(S):\n    _S['P'] = S['poses']\n",
                  "def install(S):\n    _S['P'] = S['poses']\n    _S['HOP'] = S.get('hop') or []\n")
    # 少し大きく弾む＝その区間は1小節（4拍）の頭の拍だけ浮きを3倍
    w = w.replace("    lift = -LIFT * c.height * math.sin(math.pi * p)          # 拍ちょうどで着地・拍の間で浮く\n",
                  "    lift = -LIFT * c.height * math.sin(math.pi * p)          # 拍ちょうどで着地・拍の間で浮く\n"
                  "    if any(a <= t < b for a, b in _S.get('HOP', [])) and i % 4 == 0:\n"
                  "        lift *= 3.0   # 11/16 長い出番の後半＝1小節ごとに少し大きく跳ねる\n")
    # 同じ衣装の反転どうし（w4→m4）は歩いて出入りしない＝その場でくるっと向きを変える
    w = w.replace("        tin = t0 + (DELAY if k and walker(P[k - 1][1]) and face(P[k - 1][1]) != f else 0.0)\n",
                  "        same_prev = k and P[k - 1][1][1:] == name[1:]\n"
                  "        same_next = t1 is not None and k + 1 < n and P[k + 1][1][1:] == name[1:]\n"
                  "        tin = t0 + (DELAY if k and walker(P[k - 1][1]) and face(P[k - 1][1]) != f and not same_prev else 0.0)\n"
                  "        if same_next and t >= t1:\n            continue\n")
    w = w.replace("        if t < tin + ENT:\n            u = (t - tin) / ENT\n",
                  "        if same_prev:\n            A = W / 2 + f * W * 0.08\n"
                  "        if t < tin + ENT and not same_prev:\n            u = (t - tin) / ENT\n")
    w = w.replace("        elif last or t < t1 - EXA:\n", "        elif last or same_next or t < t1 - EXA:\n")
    w = w.replace("            span = max(0.1, (t1 - EXA) - (tin + ENT)) if not last else 1.0\n            x = A + (Bx - A) * min(1.0, (t - tin - ENT) / span)\n",
                  "            span = max(0.1, (t1 - (0 if same_next else EXA)) - (tin + (0 if same_prev else ENT))) if not last else 1.0\n"
                  "            x = A + (Bx - A) * max(0.0, min(1.0, (t - tin - (0 if same_prev else ENT)) / span))\n")
    io.open(D + 'walk_char.py', 'w', encoding='utf-8').write(w)
print('ok')
