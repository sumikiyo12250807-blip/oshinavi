# -*- coding: utf-8 -*-
"""「いつまで売るか分からない」枠の一覧＝毎日売り場へ見に行く対象（2026-10-12 ユーザー
「いつまで売るかわからないものは、毎日売り場に行って確認お願いします」）

  ①saleEndUnknown ②券種名が「…発売〜」で終わる（売り場に終わりが書いていない）
  ③発売日を過ぎたのに締切なし（「…HH:MM発売」で止まっている＝ページが404・枠がページに無い）
  ※TIGET の「〜公演日 販売中」は毎朝の gate_tiget_slots が全件見るのでここでは数えない
  ※売り切れの印付き・締切の過ぎた枠は数えない

使い方: python tools/check_unknown_end.py  → 売り場ごとの一覧と --ids 用の id 列
見に行ったあと: 売っていれば残す／締切が出ていれば入れる／売り切れは印／
  無くなっていれば後継URL・他社を確かめてからその便で消す（[[feedback_gone_from_vendor_delete_daily]]）
"""
import collections
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = 'C:/Users/user/oshinavi/'
VENDORS = ('rakuten', 'eplus', 'pia', 'tiget', 'zaiko', 'livepocket', 'fany', 'l-tike')


def main():
    today = datetime.date.today().isoformat()
    s = io.open(ROOT + 'index.html', encoding='utf-8').read()
    i = s.index('const EVENTS = [') + len('const EVENTS = ')
    E, _ = json.JSONDecoder().raw_decode(s[i:])
    rows = collections.defaultdict(list)
    for e in E:
        for t in e.get('tickets') or []:
            if t.get('soldout') or (t.get('date') or '') < today:
                continue
            ty = t.get('type') or ''
            if t.get('saleEndUnknown'):
                k = 'いつまで不明'
            elif re.search(r'発売\s*〜\s*$', ty):
                k = '発売〜（終わりが書いていない）'
            elif re.search(r'\d{1,2}:\d{2}\s*発売$', ty) and t.get('startDate') and t['startDate'] < today:
                k = '発売で止まり（ページ404・枠が無い）'
            else:
                continue
            u = t.get('url') or json.dumps(e.get('links'))
            v = next((x for x in VENDORS if x in u), 'その他')
            rows[v].append((e['id'], k, ty, t.get('url') or ''))
    n = sum(len(r) for r in rows.values())
    print(f'=== いつまで売るか分からない枠 {n}（today={today}） ===')
    for v, r in sorted(rows.items()):
        print(f'-- {v} {len(r)}枠  --ids {",".join(str(x) for x in sorted({a for a, *_ in r}))}')
        for a, k, ty, u in r:
            print(f'  id{a} [{k}] {ty[:60]}  {u[:110]}')


if __name__ == '__main__':
    main()
