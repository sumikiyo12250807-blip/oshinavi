# -*- coding: utf-8 -*-
"""新着プール(genre:"new")の振り分け＝下書き _genre をそのまま genre に確定する（恒久ツール）。

memory: project_vendor_genre_autoassign
  「振り分け＝取得時に記憶したぴあカテゴリ(_genre)をそのまま適用。自分で再分類しない」
  ＝ここで判断はしない。判断は投入時の下書き補正で済ませておく（0直しにするため）。

🚨 実行はユーザーが「振り分けて」と明示してから（memory: feedback_new_pool_ok_before_assign）。
   2026-07-19 にチェック前へ振り分けて新着タブを空にする事故を起こしている。

やること:
  - genre:"new" のエントリの genre ← _genre、extraGenres ← _extraGenres
  - 下書きフィールド(_genre/_extraGenres/_piaSub/_srcgenre)を削除
  - NEW_ORDER を空にする（並び順配列だけ残ると空の新着タブになる）

使い方: python tools/assign_genres.py [--apply] [--exclude 3003,3004]
"""
import argparse
import collections
import json
import re
import sys

DRAFT_FIELDS = ('_genre', '_extraGenres', '_piaSub', '_srcgenre')
PATH = 'index.html'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--exclude', default='', help='振り分けから外すid（削除候補など）')
    args = ap.parse_args()
    skip = {int(x) for x in args.exclude.split(',') if x.strip()}

    src = open(PATH, encoding='utf-8').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    assert m, 'EVENTS配列が見つからない'
    events = json.loads(m.group(2))

    targets = [e for e in events if e.get('genre') == 'new' and e['id'] not in skip]
    if not targets:
        print('genre:"new" のエントリが無い')
        return 0

    missing = [e['id'] for e in targets if not e.get('_genre')]
    if missing:
        print(f'🚨 下書き _genre が無いエントリ {len(missing)}件 → 先に決めること: {missing}')
        return 1

    counts = collections.Counter()
    both = []
    for e in targets:
        g = e['_genre']
        e['genre'] = g
        counts[g] += 1
        extra = e.get('_extraGenres') or []
        if extra:
            e['extraGenres'] = extra
            both.append((e['id'], g, extra, e.get('name')))
        for f in DRAFT_FIELDS:
            e.pop(f, None)

    print(f'=== 振り分け {len(targets)}件 ===')
    for g, n in counts.most_common():
        print(f'   {g:10s} {n}')
    if both:
        print(f'\n--- 両方式 {len(both)}件 ---')
        for eid, g, extra, name in both:
            print(f'   id={eid} {g}+{"+".join(extra)}  {name}')
    if skip:
        print(f'\n--- 振り分けから除外 {len(skip)}件（genre:"new"のまま残る）---')
        for eid in sorted(skip):
            e = next((x for x in events if x['id'] == eid), None)
            print(f'   id={eid} {e.get("name") if e else "(見つからない)"}')

    remain = [e for e in events if e.get('genre') == 'new']
    print(f'\n新着プール残り: {len(remain)}件')

    if not args.apply:
        print('(--apply で書き込み)')
        return 0

    out = src[:m.start(2)] + json.dumps(events, ensure_ascii=False, indent=2) + src[m.end(2):]
    # NEW_ORDER は残す新着だけにする（全部振り分けたなら空）
    m2 = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])(;)', out)
    assert m2, 'NEW_ORDERが見つからない'
    keep = [e['id'] for e in remain]
    order = [i for i in json.loads(m2.group(2)) if i in keep]
    out = out[:m2.start(2)] + json.dumps(order, ensure_ascii=False) + out[m2.end(2):]
    open(PATH, 'w', encoding='utf-8').write(out)
    print(f'書き込み完了 / NEW_ORDER {len(order)}件')
    return 0


if __name__ == '__main__':
    sys.exit(main())
