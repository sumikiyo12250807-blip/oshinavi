# -*- coding: utf-8 -*-
"""検証エージェントD（12件）の独立導出値と index.html の登録値を機械照合する。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

# id: (枠数, 千秋楽, 都道府県, ジャンル, extraGenres)
D = {
    4660: (2, '2026-12-02', '北海道', 'jazz', []),
    4667: (1, '2026-11-29', '神奈川', 'classic', ['engeki']),
    4668: (2, '2026-11-03', '福岡', 'musical', []),
    4669: (1, '2026-11-20', '神奈川', 'owarai', []),
    4670: (1, '2027-01-17', '神奈川', 'owarai', []),
    4672: (1, '2026-10-24', '徳島', 'classic', ['engeki']),
    4674: (1, '2027-01-17', '東京', 'owarai', []),
    4675: (1, '2027-02-22', '東京', 'owarai', []),
    4677: (1, '2027-04-20', '東京', 'owarai', []),
    4679: (1, '2026-12-11', '東京', 'owarai', []),
    4680: (1, '2026-12-24', '東京', 'owarai', []),
    4688: (1, '2026-10-18', '京都', 'dento', []),
}

h = open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))}

ng = 0
for i, (n, last, pref, genre, extra) in sorted(D.items()):
    e = ev.get(i)
    if not e:
        print('NG id=%d : 登録に無い' % i); ng += 1; continue
    reg_n = len(e.get('tickets') or [])
    reg_last = e.get('date')
    reg_pref = (e.get('prefecture') or '').replace('都', '').replace('府', '').replace('県', '')
    reg_g = e.get('_genre')
    reg_x = e.get('_extraGenres') or []
    ok_n, ok_last = reg_n == n, reg_last == last
    ok_pref = (pref in reg_pref) or (reg_pref in pref)
    ok_g = (reg_g == genre) and (sorted(reg_x) == sorted(extra))
    flag = 'OK ' if (ok_n and ok_last and ok_pref and ok_g) else 'NG '
    if flag == 'NG ':
        ng += 1
    print('%s id=%d %-24s 枠 %d/%d %s | 千秋楽 %s/%s %s | 県 %s/%s %s | ジャンル %s%s/%s%s %s'
          % (flag, i, (e['name'] or '')[:24], reg_n, n, ok_n, reg_last, last, ok_last,
             reg_pref, pref, ok_pref, reg_g, ('+' + '+'.join(reg_x) if reg_x else ''),
             genre, ('+' + '+'.join(extra) if extra else ''), ok_g))
print('=== 不一致 %d / %d件 ===' % (ng, len(D)))
