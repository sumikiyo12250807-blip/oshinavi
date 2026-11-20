# -*- coding: utf-8 -*-
# 11/16 TikTok スポーツ（75.6 秒・96.7→96.1BPM）：shoot_badge と make_spec と kara_style を 11/16 用に差し替える
#   時刻＝lyrics_times2.txt（言葉の頭）。文言＝USLT（23 行・渡した歌詞と一致）を漢字に・名前はサイトの表記
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
sb = io.open(D + 'shoot_badge.py', encoding='utf-8').read()
old = "CID, Q, MD = 31804, 'さらば青春の光寄席', '11/14'   # 11/14 さらば青春の光寄席（一般発売 11/14 11:00・東京 LINE CUBE SHIBUYA）"
if old in sb:
    sb = sb.replace(old, "CID, Q, MD = 42584, '大相撲富士宮場所', '11/16'   # 11/16 令和九年 春巡業 大相撲富士宮場所（一般発売【座席券】11/16 10:00・静岡 富士宮市民体育館）")
io.open(D + 'shoot_badge.py', 'w', encoding='utf-8').write(sb)
assert "42584" in sb

ms = io.open(D + 'make_spec.py', encoding='utf-8').read()
a, b = ms.index('CHUNKS = ['), ms.index('LOW = {')
ms = ms[:a] + """CHUNKS = [
    [('11月+16日の', [1.2, 2.1]), ('発売の スポーツ', [5.4, 6.8]), ('言うわね', [7.8])],
    [('午前 10時は', [10.1, 10.9]), ('大相撲 春巡業', [11.7, 12.4]), ('富士宮 静岡', [13.4, 13.9])],
    [('東京女子プロレス', [14.9]), ('愛知', [17.2]), ('昼 12時は', [18.0, 18.2])],
    [('スターダム 大阪', [19.6, 20.8]), ('サガン鳥栖 対', [21.4, 22.3]), ('横浜FC 佐賀', [22.7, 24.1])],
    [('小島和哉の', [24.6]), ('ファンミーティング', [26.8]), ('千葉', [28.7])],
    [('夕方 6時は', [30.5, 31.3]), ('クボタスピアーズ', [31.9]), ('対 静岡', [33.1, 33.4]), ('ブルーレヴズ 東京', [34.1, 35.1])],
    [('夜 8時は', [35.6, 35.8]), ('西川遥輝と', [38.2]), ('松本剛の', [39.3]), ('トークショー 東京', [40.7, 42.0])],
    [('杉谷拳士も', [43.2]), ('一緒よ', [44.4]), ('ほかにも あるわ', [45.1, 46.0]), ('忘れないでね', [47.5])],
    [('声を からして', [49.7, 50.6]), ('応援したいわ', [51.6])],
    [('oshinavi+.jpで', [54.3, 55.6]), ('名前を', [57.5]), ('検索してね', [58.2])],
    [('公演と', [59.4]), ('アーティストの', [60.8]), ('紹介も 載せてるわ', [62.1, 63.2])],
    [('売り場まで', [65.0]), ('案内+するのは', [66.1, 66.5]), ('おしなび', [67.3])],
    [('oshinavi+.jp', [68.2, 70.6]), ('だわ', [72.5])],   # すちこ 11/13「検索するのは小文字だから小文字で表示して」
]
""" + ms[b:]
ms = ms.replace('LOW = {9, 10}', 'LOW = {10, 11}').replace('DUR = 67.6', 'DUR = 75.6')
ms = ms.replace("CHORUS_AT, URL_AT = chunks[9]['show'], chunks[11]['show']", "CHORUS_AT, URL_AT = chunks[10]['show'], chunks[12]['show']")
ms = ms.replace("chunks[11]['cy'] = 1080", "chunks[12]['cy'] = 1080")
ms = ms.replace("'lines': [[['11/14(土)', 999, False]], [['発売の', 999, True], ['お笑い', 999, False]]]",
                "'lines': [[['スポーツ', 999, False]], [['11/16(月)', 999, True], ['発売', 999, False]]]")
ms = ms.replace("S = {'when': '明日 11/14(土) 発売', 'kind': 'お笑い', 'name': 'さらば青春の光寄席',",
                "S = {'when': '11/16(月) 発売', 'kind': 'スポーツ', 'name': '大相撲富士宮場所',")
for need in ('LOW = {10, 11}', 'DUR = 75.6', "chunks[10]['show'], chunks[12]['show']", "chunks[12]['cy'] = 1080", "'11/16(月)'", "'大相撲富士宮場所',"):
    assert need in ms, need
io.open(D + 'make_spec.py', 'w', encoding='utf-8').write(ms)

# 明るい背景（白とピンクのキラキラ）＝字を暗く：まだ＝濃紺・歌った＝えんじ・縁は白の太め＋うっすら影（10/20・11/13 すちこ「背景がくらいよ」の直し）
ks = io.open(D + 'kara_style.py', encoding='utf-8').read()
old_k = "        todo, done, stroke = (WHITE, YEL, (20, 10, 40))   # 10/28 背景が暗い＝いつも白／黄・縁は濃紺\n        shadow = (0, 0, 0, 150)"
assert old_k in ks
ks = ks.replace(old_k, "        if low:   # タップの場面は下の暗い帯の中＝白／黄・縁は濃紺\n            todo, done, stroke, shadow = WHITE, YEL, (20, 10, 40), (0, 0, 0, 150)\n"
                "        else:     # 11/16 明るい背景＝濃紺／えんじ・縁は白・うっすら影\n            todo, done, stroke, shadow = NAVY, ENJI, WHITE, (80, 30, 90, 90)")
io.open(D + 'kara_style.py', 'w', encoding='utf-8').write(ks)
print('ok')
