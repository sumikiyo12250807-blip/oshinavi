# -*- coding: utf-8 -*-
"""9/21夜 ユーザー「足して」＝新着タブのうち9/22〜9/24発売の分を、X投稿④⑥⑨に足す。
行の形は material_b.md（新着を混ぜて作り直した素材）から。同じ興行の部・会場違いは1行にまとめる（X_SCRIPT）。
「他にも◯件」は material_b.md の数（9/23＝9件／9/24＝20件近く）。"""
import io, sys
sys.stdout.reconfigure(encoding='utf-8')


def edit(path, pairs):
    s = io.open(path, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (path, a[:30])
        s = s.replace(a, b)
    io.open(path, 'w', encoding='utf-8').write(s)
    print('直した', path)


edit('tmp/x0921/post04.txt', [
    ('【9/22(火)発売】\n11:00 フォレスタ／京都\n',
     '【9/22(火)発売】\n0:00 【DAY 3 CLOSING】MUSCLE BEACH TOKYO RETURNS 2026（BEAR’S BASH・BOY’S BASH）当日券／東京\n11:00 フォレスタ／京都\n'),
    ('18:00 櫻坂46 「15th Single BACKS LIVE!!」／東京\n',
     '18:00 櫻坂46 「15th Single BACKS LIVE!!」／東京\n18:00 Verrückt × unchained／東京\n'),
])
edit('tmp/x0921/post06.txt', [
    ('10:00 第7回 入船亭扇七ネタ下ろしひとり会 わん丈作・喪服キャバクラ他／東京\n',
     '10:00 第7回 入船亭扇七ネタ下ろしひとり会 わん丈作・喪服キャバクラ他／東京\n11:00 食欲の秋？スポーツの秋？いや、漫才の秋！！！・・・／大阪（先行）\n'),
])
edit('tmp/x0921/post09.txt', [
    ('10:00 ジャパンレプタイルズショー2027 in 東京 BIG春レプ／東京\n',
     '10:00 ジャパンレプタイルズショー2027 in 東京 BIG春レプ／東京\n'
     '10:00 青木マッチョ 初ファンイベント（第1部〜第9部）／愛知・大阪\n'
     '12:00 NMB48劇場「ここにだって天使はいる」公演／大阪（先行）\n'
     '12:00 NMB48劇場「無限大ノック」公演／大阪（先行）\n'
     '12:00 NMB48劇場「青春！恋のDestination」公演／大阪（先行）\n'),
    ('20:00 BØUQUET 惰眠-だみん- Birthday Live-／愛知\n他にも6件あるわ。', '20:00 BØUQUET 惰眠-だみん- Birthday Live-／愛知\n他にも9件あるわ。'),
    ('20:00 GLIM9 HALLOWEEN NIGHT 2026／愛媛\n他にも10件以上あるわ。', '20:00 GLIM9 HALLOWEEN NIGHT 2026／愛媛\n他にも20件近くあるわ。'),
])
