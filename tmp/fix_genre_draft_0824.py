# -*- coding: utf-8 -*-
"""新着プールの下書き _genre を、決めた結論に合わせて直す（2026-08-24 朝の振り分け前）。

ぴあカテゴリ由来の下書きが「会場の業態」や「受け皿の無さ」でズレていた分だけを補正する。
根拠＝別エージェントの独立判定＋index.html の既存先例（機械照合ずみ）。
  4979 シネマ歌舞伎上映会      engeki  → dento(+engeki)  中身が歌舞伎
  5002 塩竈 秋の酒蔵めぐり     kids    → gourmet         先例 4260 サケマルシェ
  5005 岸和田だんじり祭        fes     → dento           先例 2074 石見神楽・2531 結縁灌頂
  5010 将棋 公開模範対局       engeki  → dento           先例 3510 竜王戦 前夜祭
  5035 金シャチ横丁 ワイン魂    kids    → gourmet         先例 3926 ビアフェス
  5038 宮田愛萌 サイン本お渡し会 engeki  → fanevent        先例 4259 佐藤大樹 写真集イベント
  5045 FTISLAND               yougaku → kpop            韓国のバンド（memory: feedback_kpop_vs_yougaku）
  5089 BihokuFireworks        fes     → hanabi          花火大会（既存14件すべて hanabi）

使い方: python tmp/fix_genre_draft_0824.py [--apply]
"""
import json
import re
import sys

PATH = 'index.html'
FIX = {
    4979: ('dento', ['engeki']),
    5002: ('gourmet', None),
    5005: ('dento', None),
    5010: ('dento', None),
    5035: ('gourmet', None),
    5038: ('fanevent', None),
    5045: ('kpop', None),
    5089: ('hanabi', None),
}


def main():
    apply = '--apply' in sys.argv
    src = open(PATH, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in src else '\n'
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    assert m, 'EVENTS配列が見つからない'
    events = json.loads(m.group(2))

    hit = 0
    for e in events:
        if e['id'] not in FIX:
            continue
        if e.get('genre') != 'new':
            print('!! id=%d は新着プールに居ない（genre=%s）' % (e['id'], e.get('genre')))
            return 1
        g, extra = FIX[e['id']]
        print('id=%-5d %-8s -> %-9s %s' % (e['id'], e.get('_genre'), g, ('+' + '+'.join(extra)) if extra else ''))
        e['_genre'] = g
        if extra:
            e['_extraGenres'] = extra
        hit += 1

    if hit != len(FIX):
        print('!! 直せたのは %d/%d 件' % (hit, len(FIX)))
        return 1

    if not apply:
        print('(--apply で書き込み)')
        return 0

    dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
    open(PATH, 'w', encoding='utf-8', newline='').write(src[:m.start(2)] + dumped + src[m.end(2):])
    print('書き込み完了 %d件' % hit)
    return 0


if __name__ == '__main__':
    sys.exit(main())
