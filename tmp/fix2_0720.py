# -*- coding: utf-8 -*-
"""2026-07-20 新着バッチ2のお直し。

(1) 空カッコ会場「全国ツアー（）」5件を、ぴあ実ページの会場名で補完（全件WebFetchで裏取り済）。
    dateLabel にも会場名を足す（無いと画面で会場が分からない・7/19 キノコホテルと同型）。
(2) _piaSub が空/その他でフォールバックした下書きジャンルの補正（裏取り済みのみ）。

使い方: python tmp/fix2_0720.py [--apply]
"""
import json
import re
import sys

APPLY = '--apply' in sys.argv
PATH = 'index.html'

# id: (新しいvenue, 会場名だけの文字列(dateLabel末尾に足す))
VENUE_FIX = {
    2990: ('全国ツアー（呉信用金庫ホール／山口市民会館 大ホール）',
           '呉信用金庫ホール／山口市民会館 大ホール'),
    # 東京の2会場のみ＝「全国ツアー」ではない
    2992: ('大田区民ホール・アプリコ 大ホール／草月ホール',
           '大田区民ホール・アプリコ 大ホール／草月ホール'),
    2994: ('全国ツアー（座・高円寺1／近鉄アート館）',
           '座・高円寺1／近鉄アート館'),
    3006: ('全国ツアー（パルテノン多摩 小ホール／相模女子大学グリーンホール 多目的ホール／ほねごり杜のホールはしもと 多目的室）',
           'パルテノン多摩 小ホール／相模女子大学グリーンホール 多目的ホール／ほねごり杜のホールはしもと 多目的室'),
    3007: ('全国ツアー（アレイホール／竹風堂善光寺大門店 3F 大門ホール／DOLCE倉庫）',
           'アレイホール／竹風堂善光寺大門店 3F 大門ホール／DOLCE倉庫'),
}

GENRE_FIX = {
    2978: ('classic', '出演は札幌国際情報高校吹奏楽部の単一団体・屋内ホール＝fesの定義(複数組+屋外)に当たらない。吹奏楽なのでclassic(2932と同じ扱い)'),
    2982: ('art', 'サイン本お渡し会&撮影会＝イベント'),
    2988: ('idol', 'ふぉ～ゆ～ LIVE TOUR 2026「I♡YoU 〜ご自愛ください〜」＝舞台ではなくライブツアー'),
    3010: ('anime', 'ぴあが「アニメ・声優・ゲーム」に分類。ブルーロックのコラボ宿泊プラン'),
}


def main():
    src = open(PATH, encoding='utf-8').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    assert m, 'EVENTS配列が見つからない'
    events = json.loads(m.group(2))
    by_id = {e['id']: e for e in events}

    print('■ 空カッコ会場の補完（ぴあ実ページで裏取り済）')
    for eid, (venue, venue_only) in VENUE_FIX.items():
        e = by_id.get(eid)
        if not e:
            print(f'   🚨 id={eid} が無い')
            return 1
        print(f'   id={eid} {e.get("name")}')
        print(f'      venue: {e.get("venue")}\n          → {venue}')
        e['venue'] = venue
        dl = e.get('dateLabel') or ''
        if dl and venue_only not in dl:
            e['dateLabel'] = f'{dl} {venue_only}'
            print(f'      dateLabel: {dl}\n          → {e["dateLabel"]}')

    print('\n■ 下書きジャンルの補正（genreは"new"のまま）')
    for eid, (g, why) in GENRE_FIX.items():
        e = by_id.get(eid)
        if not e:
            print(f'   🚨 id={eid} が無い')
            return 1
        if e.get('genre') != 'new':
            print(f'   🚨 id={eid} は genre={e.get("genre")} ＝新着ではない。中止')
            return 1
        print(f'   id={eid} _genre {e.get("_genre")} → {g}')
        print(f'       ({why})')
        e['_genre'] = g

    if not APPLY:
        print('\n(--apply で書き込み)')
        return 0

    out = src[:m.start(2)] + json.dumps(events, ensure_ascii=False, indent=2) + src[m.end(2):]
    open(PATH, 'w', encoding='utf-8').write(out)
    print('\n書き込み完了')
    return 0


if __name__ == '__main__':
    sys.exit(main())
