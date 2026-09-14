# -*- coding: utf-8 -*-
"""9/13夜のX投稿（明日9/14発売）の素材を、投稿1本ずつに割って1枚にする。Fableに渡すのはこれと X_SCRIPT.md だけ。
・明日9/14発売＝その投稿のジャンルを全部（同じ時刻・名前・県・先行の行は1行にまとめる）
・9/15・9/16＝その投稿のジャンルから箱の大きい順に5件、残りは「他にも◯件以上」（10の位で切り下げ・10未満はそのまま）
🚨「発売開始」＝ticket.startDate がその日のもの。新着プール（振り分け前）は出さない。売り切れ枠は出さない。
出力: tmp/x0914/material.md
"""
import collections, datetime, io, json, os, re
DAYS = ['2026-09-14', '2026-09-15', '2026-09-16']
WD = '月火水木金土日'
GROUPS = [  # (投稿の名前, [genre...], URLのgenre)
    ('音楽（J-POP・ロック・洋楽）', ['jpop', 'rock', 'yougaku'], 'jpop'),
    ('クラシック・ジャズ・邦楽', ['classic', 'jazz', 'hougaku'], 'classic'),
    ('お笑い・落語', ['owarai'], 'owarai'),
    ('舞台（演劇・ミュージカル・伝統芸能・舞台挨拶）', ['engeki', 'musical', 'dento', 'aisatsu'], 'engeki'),
    ('スポーツ', ['sports'], 'sports'),
    ('イベント（展示・ファンイベント・キッズ・ディナーショー・花火・声優・学園祭ほか）',
     ['art', 'fanevent', 'musicetc', 'kids', 'dinnershow', 'hanabi', 'seiyuu', 'gakusai', 'enka', 'event', 'talkshow', 'circus', 'magic', 'gourmet', 'douyou', 'chanson', 'kaidan', '2.5ji', 'anime', 'idol', 'kpop', 'hiphop', 'fes', 'youtuber', 'vtuber'], 'art'),
]
BIG = ['ドーム', 'アリーナ', '国際フォーラム', '武道館', 'スタジアム', '大ホール', 'コンサートホール', '大劇場',
       '文化会館', '市民会館', '芸術劇場', '公会堂', 'サンプラザ', 'ホール']


def bigness(v):
    for i, k in enumerate(BIG):
        if k in (v or ''):
            return i
    return len(BIG)


def more(n):
    if n <= 0:
        return None
    if n < 10:
        return '他にも%d件あるわ' % n
    return '他にも%d件以上あるわ' % (n // 10 * 10)


h = io.open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
rows = {d: collections.defaultdict(list) for d in DAYS}
for e in EV:
    if e.get('genre') == 'new':
        continue
    for t in e.get('tickets') or []:
        sd = t.get('startDate')
        if sd not in rows or t.get('soldout'):
            continue
        ty = t.get('type') or ''
        m = re.search(r'(\d{1,2}):(\d{2})\s*発売', ty)
        hhmm = '%d:%s' % (int(m.group(1)), m.group(2)) if m else '?'
        mp = re.search(r'（([^（）]*?)\s*(?:R\d+年\s*)?[\d/〜～・]+(?:\s*\d{1,2}:\d{2})?公演）', ty)
        # 🚨「都」を丸ごと消すと「京都」が「京」に欠ける（9/11 に Sundae May Club／京・大阪 で発生）
        pref = re.sub(r'(東京)都|(大阪|京都)府|(\S{2,3})県', lambda m: m.group(1) or m.group(2) or m.group(3),
                      mp.group(1) if mp else (e.get('prefecture') or ''))
        senko = any(k in ty for k in ('先行', 'プレリザーブ', '抽選', 'プリセール', 'プレオーダー'))
        rows[sd][e.get('genre')].append((hhmm, e.get('name') or '', pref, e.get('venue') or '', senko))

os.makedirs('tmp/x0913', exist_ok=True)
o = io.open('tmp/x0914/material.md', 'w', encoding='utf-8')
W = o.write
W('# 9/12夜のX投稿の素材（明日 9/13(日) 発売）\n\n')
W('ここにある事実だけで書くこと。ここに無い情報（経歴・音楽的特徴・人気）は書かない。\n\n')
for gi, (title, gs, urlg) in enumerate(GROUPS, 1):
    W('\n---\n\n## まとめ枠 %d：%s\n\nURL＝ oshinavi.jp/?genre=%s&status=urgent\n' % (gi, title, urlg))
    for di, d in enumerate(DAYS):
        dt = datetime.date.fromisoformat(d)
        lab = '%d/%d(%s)' % (dt.month, dt.day, WD[dt.weekday()])
        v = [r for g in gs for r in rows[d].get(g, [])]
        if not v:
            continue
        seen, uniq = set(), []
        for r in sorted(v, key=lambda r: (int(r[0].split(':')[0]) if r[0] != '?' else 99, r[0], r[1])):
            k = (r[0], r[1], r[2], r[4])
            if k in seen:
                continue
            seen.add(k)
            uniq.append(r)
        if di == 0:
            W('\n【%s発売】（明日・全部で %d行。1行も削らない）\n' % (lab, len(uniq)))
            pick = uniq
        else:
            pick = sorted(sorted(uniq, key=lambda r: bigness(r[3]))[:5], key=lambda r: (int(r[0].split(':')[0]) if r[0] != '?' else 99, r[0]))
            W('\n【%s発売】（大物5件・箱の大きい順に選んである）\n' % lab)
        for hh, n, p, ven, s in pick:
            W('%s %s／%s%s\n' % (hh, n, p, '（先行）' if s else ''))
        if di > 0:
            mm = more(len(uniq) - len(pick))
            if mm:
                W('（%s）\n' % mm)
o.close()
print('→ tmp/x0914/material.md')
