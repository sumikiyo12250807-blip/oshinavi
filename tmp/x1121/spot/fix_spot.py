# -*- coding: utf-8 -*-
# 11/21 抜き打ちの🟠のうち、取り直しの道具で読めない売り場（FANY・TicketDive・TIGET 本文）と ぴあの主役を、係が読んだ売り場どおりに手で直す（鍵の中）
import io, os, sys, time, json
os.chdir('C:/Users/user/oshinavi')
sys.path.insert(0, 'tools')
import compact_events as C
LK = 'tmp/x1112/index.lock'
out = io.open('tmp/x1121/spot/fix_spot.txt', 'w', encoding='utf-8')
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'fix_spot21'); os.close(fd); break
    except FileExistsError:
        time.sleep(15)
try:
    t = io.open('index.html', encoding='utf-8', newline='').read()
    E = C.load(t)
    D = {e['id']: e for e in E}
    def add(i, names, front=False):
        e = D[i]
        have = (e.get('artist') or '').split('／')
        new = [n for n in names if n not in have]
        e['artist'] = '／'.join((new + have) if front else (have + new))
        out.write('%d artist → %s\n' % (i, e['artist']))
    # 29005 ぴあ：主役の大江裕が［出演］に無い（公演名＝大江裕）
    add(29005, ['大江裕'], front=True)
    # 54987 e+：長崎 3/22 の2公演のページにだけ 島田珠代
    add(54987, ['島田珠代'])
    # 47746 FANY：売り場12組・カード8組
    add(47746, ['爆ノ介（ザ・プラン9）', '隣人', '爛々 萌々', 'cacao'])
    # 43144 TIGET：出演者の欄なし・本文「楠実もな 初のバースデーソロイベント」
    assert D[43144]['artist'] == 'もなずどりーむ'
    D[43144]['artist'] = '楠実もな'
    out.write('43144 artist → 楠実もな\n')
    # 55604 TicketDive：出演に mahoroba・県が空（住所 東京都渋谷区）
    add(55604, ['mahoroba'])
    assert not D[55604].get('prefecture')
    D[55604]['prefecture'] = '東京'
    out.write('55604 prefecture → 東京\n')
    assert D[55604]['name'] == '🍁 WASURENA Autumn チェキ会 2026 🍁'
    D[55604]['name'] = '🍁 WASURENA × mahoroba Autumn チェキ会 2026 🍁'
    out.write('55604 name → 売り場どおり\n')
    s, end, _ = C.locate(t)
    t = t[:s] + C.dump(E, True, '\r\n') + t[end:]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(t)
finally:
    os.remove(LK)
