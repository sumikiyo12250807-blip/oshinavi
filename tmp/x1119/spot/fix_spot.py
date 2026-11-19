# -*- coding: utf-8 -*-
# 11/19 抜き打ちの直し（売り場の文字どおり・鍵の中・書く直前に読み直す）
import io, os, sys, time, datetime
os.chdir('C:/Users/user/oshinavi')
sys.path.insert(0, 'tools')
import pia_soldout_sweep as S
LK = 'tmp/x1112/index.lock'
T = '2026-11-19'
log = io.open('tmp/x1119/spot/fix_spot.txt', 'w', encoding='utf-8')
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'spot_fix'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    text, st, end, E = S.load()
    by = {e['id']: e for e in E}
    def W(i, what, a, b):
        log.write('id%s %s: %s → %s\n' % (i, what, a, b))
    # 2440 RENT（ぴあ）：愛知の締切は「～ 2026/11/25(水) 9:59」・大阪/福岡は「予定枚数終了」・大阪の会場
    e = by[2440]
    for t in e['tickets']:
        ty = t.get('type') or ''
        if ty.startswith('一般発売（愛知 12/4〜12/6公演）') and t.get('date') == '2026-12-03':
            W(2440, '愛知の締切', ty, '〜11/25 9:59')
            t['type'] = '一般発売（愛知 12/4〜12/6公演）〜11/25 9:59'
            t['date'] = '2026-11-25'
        if (ty.startswith('一般発売（大阪 12/11〜12/14公演）') or ty.startswith('一般発売（福岡 11/26〜11/29公演）')) and not t.get('soldout'):
            W(2440, '売り切れの印', ty, 'soldout')
            t['soldout'] = True
            t['soldoutSince'] = T
    if 'SkyシアターMBS' not in e['venue']:
        nv = e['venue'].replace('／博多座 客席1F レストラン花幸）', '／博多座 客席1F レストラン花幸／SkyシアターMBS）')
        W(2440, '会場', e['venue'], nv); e['venue'] = nv
    nl = e['dateLabel'].replace(' 東京・広島・愛知・福岡', ' 東京・広島・福岡・愛知・大阪')
    if nl != e['dateLabel']:
        W(2440, '会期の県', e['dateLabel'], nl); e['dateLabel'] = nl
    # 40695 Rei（e+）：その期間に開いているのは「プレオーダー受付」
    for t in by[40695]['tickets']:
        if (t.get('type') or '').startswith('抽選ReinyRecords先行2次（東京 R9年 3/12公演）'):
            nt = 'プレオーダー受付（東京 R9年 3/12公演）〜11/23 23:59'
            W(40695, '受付名', t['type'], nt); t['type'] = nt
    # 31834 大阪交響楽団：「［演奏］大阪交響楽団」
    W(31834, '出演者', by[31834]['artist'], '大阪交響楽団'); by[31834]['artist'] = '大阪交響楽団'
    # 20300 NGK 本公演3回目（FANY）：「[漫才・落語]…」「[新喜劇]…」
    a = '海原やすよ ともこ／タカアンドトシ／ザ・ぼんち／テンダラー／ガクテンソク／マユリカ／ビスケットブラザーズ／エバース／酒井藍／内場勝則／末成映薫／Mr.オクレ／松浦真也／森田まりこ'
    W(20300, '出演者', by[20300]['artist'], a); by[20300]['artist'] = a
    # 55779 すこフェス：渋谷VIDENT＝東京
    if not by[55779].get('prefecture'):
        W(55779, '県', '', '東京'); by[55779]['prefecture'] = '東京'
    # 7520 天王寺楽所雅亮会：「［共演］桂吉坊(ナビゲーター) / ナニワノヲト(囃子)」
    a = '天王寺楽所雅亮会／桂吉坊／ナニワノヲト'
    W(7520, '出演者', by[7520]['artist'], a); by[7520]['artist'] = a
    # 3533 布袋寅泰（ぴあまとめ b2670338）：会場6つ・会期「2026/9/5(土) ～ 2026/12/31(木)」・代表リンクを まとめページに
    e = by[3533]
    add = ['高崎芸術劇場 大劇場', '札幌文化芸術劇場hitaru', 'ロームシアター京都 メインホール', '南海浪切ホール 大ホール', '大阪城ホール', '日本武道館']
    nv = e['venue'][:-1] + ''.join('／' + v for v in add if v not in e['venue']) + '）'
    W(3533, '会場', e['venue'], nv); e['venue'] = nv
    nl = e['dateLabel'].replace('2026年9月19日(土)〜', '2026年9月5日(土)〜')
    W(3533, '会期', e['dateLabel'], nl); e['dateLabel'] = nl
    nu = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670338'
    W(3533, '代表リンク', e['links'].get('pia'), nu); e['links']['pia'] = nu
    S.save(text, st, end, E)
finally:
    os.remove(LK)
log.close()
