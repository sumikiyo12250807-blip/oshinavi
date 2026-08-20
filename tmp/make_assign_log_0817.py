# -*- coding: utf-8 -*-
"""振り分け記録 logs/assigned_YYYY-MM-DD.md を作る（新着タブが空になる代わりの「見る場所」）。
memory: feedback_new_pool_ok_before_assign（C 後から見られるリンクを残す）"""
import re, json, io, sys
sys.stdout.reconfigure(encoding='utf-8')

EXCLUDE = {4377, 4400, 4417, 4418}
GENRE_JA = {'jpop': 'J-POP', 'kpop': 'K-POP', 'classic': 'クラシック', 'jazz': 'ジャズ',
            'owarai': 'お笑い', 'anime': 'アニメ', 'engeki': '演劇', 'fes': 'フェス',
            'yougaku': '洋楽', 'musical': 'ミュージカル', 'idol': 'アイドル'}

raw = io.open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', raw, re.S).group(1))
NEW = [e for e in EV if e.get('genre') == 'new']

rows, held = [], []
for e in NEW:
    g = e.get('_genre') or '-'
    url = (e.get('links') or {}).get('pia') or (e.get('links') or {}).get('eplus') or ''
    row = (e['id'], (e.get('artist') or e.get('name') or ''), g, e.get('dateLabel') or '',
           e.get('prefecture') or '', url)
    (held if e['id'] in EXCLUDE else rows).append(row)

rows.sort(key=lambda r: (r[2], r[0]))

out = []
out.append('# 2026-08-17 新着の振り分け（%d件）\n' % len(rows))
out.append('前夜（8/16）に投入した50件のうち %d件を正式ジャンルへ移した記録。' % len(rows))
out.append('機械の再照合（reconcile --new：OK50・エラー0）と、別エージェントの独立検品を通したうえで実行。\n')
out.append('| 公演名 | ジャンル | 日程 | 県 | URL |')
out.append('|---|---|---|---|---|')
for eid, name, g, dl, pref, url in rows:
    out.append('| %s | %s | %s | %s | %s |' % (
        name.replace('|', '｜'), GENRE_JA.get(g, g), dl.replace('|', '｜'), pref, url))

out.append('\n---\n')
out.append('## ⚠️ 振り分けずプールに残したもの（%d件）\n' % len(held))
out.append('ジャンルの判断がつかない・掲載可否そのものを相談したいもの。**新着タブに残っている**わ。\n')
out.append('| 公演名 | 何を相談したいか | URL |')
out.append('|---|---|---|')
ASK = {
    4377: 'ぴあの先行が8/16で終わり、**残るのは駐車券2枚だけ**＝入場券が1枚も買えない。載せ続けるか。会場表記も「全国ツアー（駐車場…）」と誤り',
    4400: '何のイベントか判別できない（岐阜市文化センター 11/28-29・先行だけ受付中）。ジャンルが決められない',
    4417: '韓国の歌手のワールドツアー45周年公演。K-POPに入れるか、歌謡寄りで別扱いにするか',
    4418: 'ぴあのカテゴリは「演劇/パフォーマンス」だが、5か月ロングランの暗闇ダンス体験型。art か kids 寄りではという指摘あり',
}
for eid, name, g, dl, pref, url in held:
    out.append('| %s | %s | %s |' % (name.replace('|', '｜'), ASK.get(eid, ''), url))

io.open('logs/assigned_2026-08-17.md', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('wrote logs/assigned_2026-08-17.md （振り分け%d件 / 保留%d件）' % (len(rows), len(held)))
