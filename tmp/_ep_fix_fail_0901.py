# -*- coding: utf-8 -*-
"""reconcile_eplus の FAIL 6件を、実ページで確認した結果にそろえる（2026-09-01）。

  6188 ザ・ピアノエラ … P021003 は 12/5〜12/6 の2日通し券・P021001 は 12/5 16:00 の単日
  6189 ブザフェス    … Streaming+ の配信チケット（アーカイブ〜9/6 23:59）。県が空で「（ 8/31公演）」と出ていた
  6190 Milky        … <特典会>ページ(P021002)は窓ゼロ＝死枠なので2枠を落とす
  6217 簡秀吉トークショー … 実ページの窓ゼロ＝買える枠なし → エントリごと落とす
  6242 渡辺真知子    … 大阪 10/20 17:30 のページは窓ゼロ＝死枠なので1枠を落とす
"""
import datetime
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

RETYPE = {
    (6188, 'https://eplus.jp/sf/detail/0743570001-P0030010P021003', '2026-12-01'):
        '先着一般発売（東京都 12/5〜12/6公演）〜12/1 18:00',
    (6188, 'https://eplus.jp/sf/detail/0743570001-P0030010P021001', '2026-12-01'):
        '先着一般発売（東京都 12/5 16:00公演）〜12/1 18:00',
    (6189, 'https://eplus.jp/sf/detail/4536580001-P0030002P021001', '2026-09-06'):
        '＜配信チケット＞受付【動画配信】【アーカイブ】（全国 8/31公演）〜9/6 18:00',
}
DROP = {
    (6190, 'https://eplus.jp/sf/detail/4572850001-P0030002P021002', '2026-09-02'),
    (6190, 'https://eplus.jp/sf/detail/4572850001-P0030002P021002', '2026-09-01'),
    (6242, 'https://eplus.jp/sf/detail/0025220003-P0030073P021001', '2026-10-13'),
}
DROP_ENTRY = {6217}

src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
EVENTS = json.loads(m.group(2))

out, nre, ndrop, nent = [], 0, 0, 0
for e in EVENTS:
    if e.get('id') in DROP_ENTRY:
        print(f"エントリ削除 id{e['id']} {e.get('artist')}（実ページに買える枠なし）")
        nent += 1
        continue
    tks = []
    for t in e.get('tickets', []):
        k = (e.get('id'), t.get('url'), t.get('date'))
        if k in DROP:
            print(f"枠削除 id{e['id']} {t['type']}")
            ndrop += 1
            continue
        if k in RETYPE:
            print(f"id{e['id']}\n  旧 {t['type']}\n  新 {RETYPE[k]}")
            t['type'] = RETYPE[k]
            nre += 1
        tks.append(t)
    if 'tickets' in e:
        e['tickets'] = tks
    out.append(e)

# 6189 は会場が空・県が「全国」なので dateLabel をそろえる
for e in out:
    if e.get('id') == 6189:
        e['dateLabel'] = '2026年8月31日(月) 全国 配信'
        e['venue'] = '配信'
        e['prefecture'] = '全国'
        print('id6189 dateLabel/venue を「配信」にそろえた')

NL = '\r\n' if '\r\n' in src else '\n'
open(f'index.html.bak_{datetime.date.today():%m%d}_epfail', 'w', encoding='utf-8', newline='').write(src)
body = json.dumps(out, ensure_ascii=False, indent=2).replace('\n', NL)
new = src[:m.start()] + m.group(1) + body + m.group(3) + src[m.end():]
# NEW_ORDER から消したエントリを外す
keep = {e['id'] for e in out if e.get('genre') == 'new'}
m2 = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])(;)', new)
order = [i for i in json.loads(m2.group(2)) if i in keep]
new = new[:m2.start(2)] + json.dumps(order, ensure_ascii=False) + new[m2.end(2):]
open('index.html', 'w', encoding='utf-8', newline='').write(new)
print(f'\n✅ 表記直し {nre}枠 / 枠削除 {ndrop} / エントリ削除 {nent} / NEW_ORDER {len(order)}件')
