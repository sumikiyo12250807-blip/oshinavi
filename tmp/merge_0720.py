# -*- coding: utf-8 -*-
"""2026-07-20 新着バッチの統合。

dup_scan.py --new が拾った「同一興行が券種違いで別エントリになっている」組を
1エントリにまとめ、券種を tickets に全展開する（memory: feedback_tour_consolidate /
feedback_tickets_all_expand / feedback_tour_per_ticket_url）。

- 親 = グループ先頭のid。name/artist/venue を興行名に直す。
- 各券種は ticket として残し、type に〔券種名〕を挿し、url に元エントリの個別ぴあURLを付ける。
- 子エントリは削除。NEW_ORDER も揃える（並び順配列だけ残ると新着タブが壊れる）。

使い方: python tmp/merge_0720.py [--apply]
"""
import json
import re
import sys

APPLY = '--apply' in sys.argv
PATH = 'index.html'

# (親id, [統合する全id], 新しい name/artist, 新しい venue or None, {id: 券種名})
GROUPS = [
    (2953,
     [2953, 2954, 2955, 2956],
     'ニジゲンノモリ ゴジラ迎撃作戦～国立ゴジラ淡路島研究センター～',
     None,
     {2953: 'ゴールドチケット', 2954: 'VIPジャーニーパス',
      2955: 'プレミアムチケット', 2956: 'ライトチケット'}),
    (2958,
     [2958, 2959, 2960, 2961, 2962],
     'ニジゲンノモリ NARUTO&BORUTO忍里（SHINOBI-ZATO）',
     None,
     {2958: '我愛羅プレミアムチケット', 2959: 'ゴールドチケット',
      2960: 'ナルトプレミアムチケット', 2961: 'VIPジャーニーパス',
      2962: 'ライトチケット'}),
    (2950,
     [2950, 2951],
     'ニジゲンノモリ クレヨンしんちゃんアドベンチャーパーク',
     None,
     {2950: 'ゴールドチケット', 2951: 'ライトチケット'}),
    (2942,
     [2942, 2943, 2944, 2945, 2946, 2947],
     'Gecko Market 2026',
     '東京都立産業貿易センター台東館 4階・5階展示室',
     {2942: '5F 一般入場', 2943: '5F 最終入場', 2944: '5F 先行入場',
      2945: '4F 一般入場', 2946: '4F 最終入場', 2947: '4F 先行入場'}),
    (2933,
     [2933, 2934],
     '第39回 東京都マーチングコンテスト',
     None,
     {2933: '高等学校以上の部', 2934: '中学生の部'}),
]


def label_type(t, kenshu):
    """type の販売区分の直後に〔券種名〕を挿す。
    「一般発売（東京 9/13公演）8/8 10:00発売」→「一般発売〔5F 一般入場〕（東京 9/13公演）…」
    公演日カッコの形は崩さない（check_badges.py のオレンジ強調判定が見る）。"""
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
                    t['url'] = url          # 券種ごとに個別ぴあページへ飛ばす
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

    # NEW_ORDER から消えたidを除く（並び順配列だけ残ると新着タブが壊れる）
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
