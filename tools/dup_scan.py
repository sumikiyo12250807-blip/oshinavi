# -*- coding: utf-8 -*-
"""重複スキャン（恒久ツール・新着投入前チェック）。

「会場＋公演日」の一致で **表記違いの二重登録** を洗う。
eventCd/公演名の完全一致だけを見ていた朝のチェックでは
  大西宇宙（Br） ⇔ 大西宇宙 バリトン・リサイタル
のような組がすり抜け、2026-07-19 に10件の重複が見つかった（原型 tmp/dupscan_0719.py）。

使い方:
  python tools/dup_scan.py            # DB全件（既存同士も含めて洗う）
  python tools/dup_scan.py --new      # 新着(genre:"new")が絡む組だけ ← 投入前チェックはこれ

終了コード: 疑いの組が1件でもあれば 1（投入前ゲートに使える）。

【注意】同日同会場でも **昼夜公演・車椅子席の別カード** など正当な組がある。
機械は候補を出すだけ。消すかどうかは必ず人が枠の中身を見て決めること。
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_expired import extract_events_array  # 配列抽出は既存ロジックを流用

# 会場がまとめ表記のツアーは、別ツアー同士が偶然当たるので突合対象から外す
TOUR_VENUE_MARKERS = ('全国ツアー', 'ほか')


def event_cds(e):
    """エントリが持つ ぴあ eventCd/eventBundleCd を全部集める（links.pia＋各枠のURL）。"""
    cds = set()
    urls = [(e.get('links') or {}).get('pia')]
    urls += [t.get('url') for t in e.get('tickets', [])]
    for u in urls:
        if u:
            cds |= set(re.findall(r'event(?:Bundle)?Cd=([A-Za-z0-9]+)', u))
    return cds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--file', default='index.html')
    ap.add_argument('--new', action='store_true',
                    help='新着(genre:"new")が絡む組だけ表示（投入前チェック用）')
    args = ap.parse_args()

    events = extract_events_array(args.file)
    print(f'全 {len(events)} 件（{args.file}）\n')

    groups = {}
    for e in events:
        venue, date = e.get('venue'), e.get('date')
        if not venue or not date:
            continue
        if any(mk in venue for mk in TOUR_VENUE_MARKERS):
            continue
        groups.setdefault((venue, date), []).append(e)

    hits = 0
    for (venue, date), lst in sorted(groups.items(), key=lambda x: x[0][1]):
        if len(lst) < 2:
            continue
        if args.new and not any(e.get('genre') == 'new' for e in lst):
            continue
        # eventCd を共有していれば同一興行の分割登録＝別枠として正当なことが多いが、
        # 判断材料として出すだけで除外はしない（消す判断は人）
        shared = set.intersection(*[event_cds(e) or set() for e in lst]) if len(lst) > 1 else set()
        hits += 1
        print(f'■ {venue} / {date}' + ('  ※eventCd共有' if shared else ''))
        for e in lst:
            mark = '🆕' if e.get('genre') == 'new' else '  '
            print(f'  {mark} id={e["id"]} [{e.get("genre")}] {e.get("name")}')
            print(f'       枠{len(e.get("tickets", []))} cd={sorted(event_cds(e))}')
            if e.get('dateLabel'):
                print(f'       dateLabel: {e["dateLabel"]}')
        print()

    scope = '新着が絡む組' if args.new else '会場＋公演日が重なる組'
    print(f'=== {scope} {hits} 件 ===')
    if hits:
        print('※ 枠の中身を目視して、本当に同じ興行かを確認すること（昼夜公演/車椅子席は正当）')
    return 1 if hits else 0


if __name__ == '__main__':
    sys.exit(main())
