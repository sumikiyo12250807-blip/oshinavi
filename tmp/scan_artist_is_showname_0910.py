# -*- coding: utf-8 -*-
"""artist に公演名が入っているエントリを洗い出す。

きっかけ＝2026-09-09 夜にユーザーが発見。id4119 は artist も name も
「JUNICHI INAGAKI Christmas Dinner Show」で、サイトで「稲垣潤一」を検索しても出てこなかった。
検索候補は artist から作るので直撃する。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 公演名にしか出てこない語（アーティスト名にこれが入っていたら公演名の流用を疑う）
SHOW_WORDS = [
    'コンサート', 'ツアー', 'TOUR', 'Tour', 'LIVE TOUR', '公演', '単独', 'ライブ', 'LIVE',
    'Live', 'ディナーショー', 'Dinner Show', 'DINNER SHOW', 'ディナーショウ',
    'リサイタル', 'RECITAL', 'Recital', '発売記念', '記念公演', 'フェス', 'FES', 'Festival',
    'まつり', '祭り', '演奏会', '定期公演', '特別公演', '舞台', '公開収録', 'SHOW', 'Show',
    '～', '〜', 'vol.', 'Vol.', 'VOL.', '第', '回',
]


def main():
    h = open('index.html', encoding='utf-8').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    events = json.loads(m.group(2))

    hit = []
    for e in events:
        a = (e.get('artist') or '').strip()
        n = (e.get('name') or '').strip()
        if not a or a != n:
            continue
        w = [x for x in SHOW_WORDS if x in a]
        if not w:
            continue
        hit.append((e, w))

    with open('tmp/artist_is_showname_0910.txt', 'w', encoding='utf-8') as f:
        f.write('artist == name かつ公演名らしい語を含む: %d件 / 全%d件\n' % (len(hit), len(events)))
        for e, w in sorted(hit, key=lambda x: x[0]['id']):
            ls = e.get('links') or {}
            u = ls.get('pia') or ls.get('eplus') or ls.get('rakuten') or ls.get('lawson') or ''
            f.write('\nid=%-5s [%s] %s\n' % (e['id'], e.get('genre'), e['artist']))
            f.write('   語=%s\n' % '/'.join(w[:5]))
            f.write('   %s\n' % u)
    print('artist に公演名らしい語が入っているエントリ %d件 / 全%d件 → tmp/artist_is_showname_0910.txt'
          % (len(hit), len(events)))


if __name__ == '__main__':
    main()
