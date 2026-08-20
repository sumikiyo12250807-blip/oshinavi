# -*- coding: utf-8 -*-
"""2026-07-20 2周目総点検のお直し。

(1) id=2931 第69回東北吹奏楽コンクール
    venue が「全国ツアー（…）」になっていたが、実態は 現地1会場(岩手)＋動画配信。
    ぴあ実ページで裏取り済（現地=トーサイクラシックホール岩手 大ホール 8/22-23、
    配信=PIA LIVE STREAM）。dateLabel に会場名が無い型（2026-07-19 キノコホテルと同じ）も直す。

(2) _piaSub が空/「その他」でフォールバックした下書きジャンルの補正。
    ぴあカテゴリが取れている22件には触らない（memory: project_vendor_genre_autoassign）。
    genre は "new" のままで、直すのは下書きの _genre だけ。

使い方: python tmp/fix_0720.py [--apply]
"""
import json
import re
import sys

APPLY = '--apply' in sys.argv
PATH = 'index.html'

VENUE_2931 = 'トーサイクラシックホール岩手 大ホール／PIA LIVE STREAM（動画配信）'
DATELABEL_2931 = f'2026年8月22日(土)〜2026年8月23日(日) 岩手 {VENUE_2931}'

# id: (新しい_genre, 理由)  ※裏取り済みのものだけ
GENRE_FIX = {
    2915: ('kids', '屋内小ホール・3歳以上有料の体験型ファミリーコンサート＝fesの定義(複数組+屋外)に当たらない'),
    2942: ('art', 'ヤモリの展示即売会・ぴあ「イベント/イベントその他」'),
    2948: ('art', '日本酒イベント(商店街・飲食チケット10枚綴り)＝音楽フェスではない'),
    2949: ('art', '美術館の展覧会'),
    2950: ('art', 'ニジゲンノモリのテーマパーク入場券＝既存ドラクエ(2823-2825)がartで統一'),
    2952: ('kids', '子ども向け映画上映会(かいけつゾロリ)'),
    2953: ('art', 'ニジゲンノモリのテーマパーク入場券'),
    2958: ('art', 'ニジゲンノモリのテーマパーク入場券'),
    2963: ('art', '展覧会(平成レトロ展)'),
    2964: ('seiyuu', 'ぴあが「アニメ・声優・ゲーム」に分類・出演は声優4名。bundleページでカテゴリが取れず空だった分'),
}
# extraGenres の追加（両方式・memory: feedback_genre_both_when_unclear）
EXTRA_FIX = {
    2950: ['kids'],   # クレヨンしんちゃん＝子ども連れが探す
}


def main():
    src = open(PATH, encoding='utf-8').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    assert m, 'EVENTS配列が見つからない'
    events = json.loads(m.group(2))
    by_id = {e['id']: e for e in events}

    e = by_id.get(2931)
    assert e, 'id=2931が無い'
    print('■ id=2931 第69回東北吹奏楽コンクール')
    print(f'   venue: {e.get("venue")}\n       → {VENUE_2931}')
    print(f'   dateLabel: {e.get("dateLabel")}\n       → {DATELABEL_2931}')
    e['venue'] = VENUE_2931
    e['dateLabel'] = DATELABEL_2931

    print('\n■ 下書きジャンルの補正（genreは"new"のまま）')
    for eid, (g, why) in GENRE_FIX.items():
        ev = by_id.get(eid)
        if not ev:
            print(f'   🚨 id={eid} が無い')
            return 1
        if ev.get('genre') != 'new':
            print(f'   🚨 id={eid} は genre={ev.get("genre")} ＝新着ではない。中止')
            return 1
        print(f'   id={eid} _genre {ev.get("_genre")} → {g}')
        print(f'       ({why})')
        ev['_genre'] = g
        if eid in EXTRA_FIX:
            ev['_extraGenres'] = EXTRA_FIX[eid]
            print(f'       + _extraGenres={EXTRA_FIX[eid]}')

    if not APPLY:
        print('\n(--apply で書き込み)')
        return 0

    out = src[:m.start(2)] + json.dumps(events, ensure_ascii=False, indent=2) + src[m.end(2):]
    open(PATH, 'w', encoding='utf-8').write(out)
    print('\n書き込み完了')
    return 0


if __name__ == '__main__':
    sys.exit(main())
