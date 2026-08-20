# -*- coding: utf-8 -*-
"""検証エージェントC（13件）の独立導出値と index.html の登録値を機械照合する。
ジャンルが「表に無い」と返ってきたものは判定を保留（None）にして、相談に回す。
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

# id: (枠数, 千秋楽, 都道府県, ジャンル or None=表に無い)
C = {
    4639: (1, '2027-01-23', '神奈川', None),
    4642: (1, '2026-12-06', '神奈川', 'dento'),
    4644: (1, '2027-01-15', '東京', 'dento'),
    4645: (1, '2027-01-16', '東京', 'dento'),
    4646: (1, '2027-01-26', '兵庫', 'jpop'),
    4647: (1, '2026-11-09', '愛知', 'jpop'),
    4648: (1, '2026-12-07', '愛知', 'jpop'),
    4652: (1, '2026-10-02', '愛知', 'jpop'),
    4653: (1, '2026-10-05', '愛知', 'jpop'),
    4654: (1, '2026-10-16', '愛知', 'jpop'),
    4655: (1, '2026-12-14', '愛知', 'jpop'),
    4656: (1, '2026-11-07', '愛知', 'jpop'),
    4657: (1, '2026-11-03', '岡山', 'jazz'),
}

h = open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))}

ng = hold = 0
for i, (n, last, pref, genre) in sorted(C.items()):
    e = ev.get(i)
    if not e:
        print('NG id=%d : 登録に無い' % i); ng += 1; continue
    reg_n = len(e.get('tickets') or [])
    reg_last = e.get('date')
    reg_pref = (e.get('prefecture') or '').replace('都', '').replace('府', '').replace('県', '')
    reg_g = e.get('_genre')
    ok_n, ok_last = reg_n == n, reg_last == last
    ok_pref = (pref in reg_pref) or (reg_pref in pref)
    if genre is None:
        ok_g, mark = None, '⏸相談'
        hold += 1
    else:
        ok_g = (reg_g == genre)
        mark = 'OK ' if (ok_n and ok_last and ok_pref and ok_g) else 'NG '
        if mark == 'NG ':
            ng += 1
    print('%s id=%d %-22s 枠 %d/%d %s | 千秋楽 %s/%s %s | 県 %s/%s %s | ジャンル 登録%s / 検証%s %s'
          % (mark, i, (e['name'] or '')[:22], reg_n, n, ok_n, reg_last, last, ok_last,
             reg_pref, pref, ok_pref, reg_g, genre, ok_g))
print('=== 不一致 %d / 相談 %d / 全%d件 ===' % (ng, hold, len(C)))
