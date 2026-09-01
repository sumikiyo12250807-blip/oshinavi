# -*- coding: utf-8 -*-
"""同じ会場・同じ日に開演時刻が2種類以上ある公演のバッジに、開演時刻を入れる。
条件は feedback_same_day_show_time_badge の2つだけ（増やさない）。
時刻は実ページのJSON-LDから取る（推測しない）。

  python tmp/fix_showtime_0902.py          # 変更内容を出すだけ
  python tmp/fix_showtime_0902.py --apply  # index.html に書き戻す
"""
import re, json, sys
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
from eplus_harvest import fetch, parse_ld

TARGETS = {5996: [0, 1, 2, 3, 4, 5, 6, 7], 6013: [0, 1], 6014: [0, 1], 6019: [0, 1]}
APPLY = '--apply' in sys.argv

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))
by = {e['id']: e for e in EV}
cache = {}
changed = 0
for eid, tis in TARGETS.items():
    e = by[eid]
    print(f'=== id{eid} {e.get("artist")}')
    for ti in tis:
        t = e['tickets'][ti]
        u = t.get('url') or ''
        if u not in cache:
            lds = parse_ld(fetch(u))
            cache[u] = lds[0] if len(lds) == 1 else {}
        L = cache[u]
        tm = (L or {}).get('time') or ''
        if not re.fullmatch(r'\d{1,2}:\d{2}', tm):
            print(f'  t{ti} !! LDに開演時刻が無い（{tm!r}）→ 触らない')
            continue
        old = t.get('type') or ''
        # 「（東京都 10/11公演）」→「（東京都 10/11 16:00公演）」。既に時刻があるものは触らない
        new = re.sub(r'([（(][^（）()]*?\d{1,2}/\d{1,2})公演([）)])',
                     lambda mm: f'{mm.group(1)} {tm}公演{mm.group(2)}', old, count=1)
        if new == old:
            print(f'  t{ti} 変化なし（形が違う/既に時刻あり）: {old}')
            continue
        print(f'  t{ti} {old}')
        print(f'    → {new}')
        t['type'] = new
        changed += 1
print(f'\n書き換え対象 {changed}枠  APPLY={APPLY}')
if APPLY and changed:
    out = h[:m.start()] + m.group(1) + json.dumps(EV, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]
    open('index.html.bak_0902_showtime', 'w', encoding='utf-8').write(h)
    open('index.html', 'w', encoding='utf-8').write(out)
    print('index.html を更新（backup: index.html.bak_0902_showtime）')
