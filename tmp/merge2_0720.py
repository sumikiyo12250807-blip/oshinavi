# -*- coding: utf-8 -*-
"""2026-07-20 新着バッチ2の統合。

ブルーロック×サンシャインシティプリンスホテルのコラボルームが
「部屋タイプ違い」で5エントリに割れていたので1枚にまとめ、部屋を tickets に全展開する
（memory: feedback_tour_consolidate / feedback_tickets_all_expand / feedback_tour_per_ticket_url）。

使い方: python tmp/merge2_0720.py [--apply]
"""
import json
import re
import sys

APPLY = '--apply' in sys.argv
PATH = 'index.html'

GROUPS = [
    (3010,
     [3010, 3011, 3012, 3013, 3014],
     'ブルーロック×サンシャインシティプリンスホテル',
     None,
     {3010: '潔 世一／糸師 凛ROOM', 3011: '潔 世一／凪 誠士郎ROOM',
      3012: '潔 世一／氷織 羊ROOM', 3013: '糸師 凛／糸師 冴ROOM',
      3014: '凪 誠士郎／御影 玲王ROOM'}),
]


def label_type(t, kenshu):
    m = re.match(r'^(.+?)(（)', t)
    if not m:
        return f'{t}〔{kenshu}〕'
    return f'{m.group(1)}〔{kenshu}〕' + t[m.end(1):]


def main():
    src = open(PATH, encoding='utf-8').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    assert m, 'EVENTS配列が見つからない'
    events = json.loads(m.group(2))
    by_id = {e['id']: e for e in events}

    removed = set()
    for parent_id, ids, name, venue, kenshu_map in GROUPS:
        parent = by_id.get(parent_id)
        if not parent:
            print(f'🚨 親 id={parent_id} が無い')
            return 1
        merged = []
        for i in ids:
            e = by_id.get(i)
            if not e:
                print(f'🚨 id={i} が無い')
                return 1
            url = (e.get('links') or {}).get('pia')
            for t in e.get('tickets', []):
                t = dict(t)
                t['type'] = label_type(t['type'], kenshu_map[i])
                if url:
                    t['url'] = url
                merged.append(t)
            if i != parent_id:
                removed.add(i)
        parent['name'] = name
        parent['artist'] = name
        if venue:
            parent['venue'] = venue
        parent['tickets'] = merged
        print(f'■ id={parent_id} {name}')
        print(f'   {len(ids)}件 → 1件 / 枠 {len(merged)}')
        for t in merged:
            print(f'     - {t["type"]}')
        print()

    events = [e for e in events if e['id'] not in removed]

    m2 = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])(;)', src)
    assert m2, 'NEW_ORDERが見つからない'
    order = json.loads(m2.group(2))
    new_order = [i for i in order if i not in removed]

    print(f'=== 統合 {len(GROUPS)}組 / 削除 {len(removed)}件 / 総 {len(events)}件 '
          f'/ NEW_ORDER {len(order)}→{len(new_order)} ===')
    if not APPLY:
        print('(--apply で書き込み)')
        return 0

    out = src[:m.start(2)] + json.dumps(events, ensure_ascii=False, indent=2) + src[m.end(2):]
    m2b = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])(;)', out)
    out = out[:m2b.start(2)] + json.dumps(new_order, ensure_ascii=False) + out[m2b.end(2):]
    open(PATH, 'w', encoding='utf-8').write(out)
    print('書き込み完了')
    return 0


if __name__ == '__main__':
    sys.exit(main())
