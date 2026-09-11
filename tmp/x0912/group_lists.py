# -*- coding: utf-8 -*-
"""X投稿のリストを「アーティストごとに1行・地域をまとめる」形に直す（2026-09-11 ユーザー指示
「リストなんだけど、長くなりすぎだから、アーティストごとにまとめて、地域を書けばいい」）。
・まとめる単位＝（時刻・名前・先行かどうか）が同じ行。時刻が違えば別の行のまま（発売時刻は大事なので潰さない）
・地域は出てきた順に「・」でつなぐ。同じ県は1回だけ
・並びは元の順（最初に出てきた位置）
使い方: python tmp/x0912/group_lists.py [--apply]
"""
import glob, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
LINE = re.compile(r'^((?:\d{1,2}:\d{2})|時刻未定) (.+)／([^／]+?)(（先行）)?$')
# 同じアーティスト・同じ催しなのに登録の名前の書き方が違うもの（1行にまとめるために名前をそろえる）
ALIAS = {
    'Chage<振替公演>': 'Chage',
    'アンジュルム 2026秋 風林火山・弐': 'アンジュルム',
    '矢野顕子リサイタル in 音楽堂 2026': '矢野顕子',
    '時代を彩る歌姫たち': 'サーカス/庄野真代/渡辺真知子 時代を彩る歌姫たち',
    '坂東玉三郎 プレミアムシンフォニックコンサート with 春風亭小朝': '坂東玉三郎',
    '坂東玉三郎（人間国宝・歌舞伎俳優）～お話と素踊り～': '坂東玉三郎',
    'D.I.D全日本モトクロス選手権シリーズ 2026 第9戦 第64回MFJ-GPモトクロス大会 グッズ付き観戦券': 'D.I.D全日本モトクロス選手権シリーズ 2026 第9戦 第64回MFJ-GPモトクロス大会',
    'D.I.D全日本モトクロス選手権シリーズ 2026 第9戦 第64回MFJ-GPモトクロス大会 観戦券': 'D.I.D全日本モトクロス選手権シリーズ 2026 第9戦 第64回MFJ-GPモトクロス大会',
    '浦和レッズ対V・ファーレン長崎 明治安田J1リーグ': '浦和レッズ 明治安田J1リーグ（長崎戦・千葉戦・セレッソ大阪戦）',
    '浦和レッズ対ジェフユナイテッド千葉 明治安田J1リーグ': '浦和レッズ 明治安田J1リーグ（長崎戦・千葉戦・セレッソ大阪戦）',
    '浦和レッズ対セレッソ大阪 明治安田J1リーグ': '浦和レッズ 明治安田J1リーグ（長崎戦・千葉戦・セレッソ大阪戦）',
    '大樹生命 Wリーグ 2026-27 レギュラーシーズン 第1週 [加古川]': '大樹生命 Wリーグ 2026-27 レギュラーシーズン',
    '大樹生命 Wリーグ 2026-27 レギュラーシーズン 第3週 [廿日市]': '大樹生命 Wリーグ 2026-27 レギュラーシーズン',
    '大樹生命 Wリーグユナイテッドカップ 2026-27 グループステージ／駒沢体育館（A会場）': '大樹生命 Wリーグユナイテッドカップ 2026-27 グループステージ',
    '大樹生命 Wリーグユナイテッドカップ 2026-27 グループステージ／駒沢屋内球技場（B会場）': '大樹生命 Wリーグユナイテッドカップ 2026-27 グループステージ',
    'ジャパンレプタイルズショー2027 in 京都 京レプ': 'ジャパンレプタイルズショー2027',
    'ジャパンレプタイルズショー2027 in 愛知 セントレア': 'ジャパンレプタイルズショー2027',
    'ジャパンレプタイルズショー2027 in 札幌 北レプ春': 'ジャパンレプタイルズショー2027',
    'ジャパンレプタイルズショー2027 in 熊本 熊レプ': 'ジャパンレプタイルズショー2027',
    'ジャパンレプタイルズショー2027 冬レプ': 'ジャパンレプタイルズショー2027',
    'siruko Fan Meeting Tour 2026 しるこの部屋～みんなでしるこの部屋～': 'siruko Fan Meeting Tour 2026 しるこの部屋',
    'siruko Fan Meeting Tour 2026 ～みんなでしるこの部屋～': 'siruko Fan Meeting Tour 2026 しるこの部屋',
    '二見颯一／青山新': '二見颯一&青山新 ライブツアー2026',
    '就実大学なでしこ祭 志田未来 トークショー': '志田未来 トークショー',
    'くらしき作陽大学・作陽短期大学翔陽祭 志田未来 トークショー': '志田未来 トークショー',
}


def regroup(lines):
    out, idx = [], {}
    for ln in lines:
        m = LINE.match(ln)
        if not m:
            out.append(ln)
            continue
        t, name, prefs, senko = m.group(1), m.group(2), m.group(3), m.group(4) or ''
        name = ALIAS.get(name, name)
        key = (t, name, senko)
        if key in idx:
            item = out[idx[key]]
        else:
            item = [t, name, [], senko]
            idx[key] = len(out)
            out.append(item)
        for p in prefs.split('・'):
            if p and p not in item[2]:
                item[2].append(p)
    # 「配信」は県ではないので最後に回す
    return [x if isinstance(x, str) else '%s %s／%s%s' % (
        x[0], x[1], '・'.join([p for p in x[2] if p != '配信'] + [p for p in x[2] if p == '配信']), x[3]) for x in out]


for f in sorted(glob.glob('tmp/x0912/post*.txt')):
    t = io.open(f, encoding='utf-8-sig').read()
    L = t.split('\n')
    new, block = [], []
    for ln in L + ['']:
        if LINE.match(ln):
            block.append(ln)
            continue
        if block:
            new += regroup(block)
            block = []
        new.append(ln)
    new = new[:-1]
    before = sum(1 for x in L if LINE.match(x))
    after = sum(1 for x in new if LINE.match(x))
    print('%s  リスト %d行 → %d行 ／ %d字 → %d字' % (f[-10:], before, after, len(t), len('\n'.join(new))))
    if '--apply' in sys.argv:
        io.open(f, 'w', encoding='utf-8', newline='').write('\n'.join(new))
