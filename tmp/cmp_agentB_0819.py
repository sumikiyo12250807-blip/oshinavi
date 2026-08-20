# -*- coding: utf-8 -*-
"""検証エージェントB（13件）の独立導出値と index.html の登録値を機械照合する。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

# id: (枠数, 千秋楽, 都道府県, ジャンル)
B = {
    4623: (1, '2026-11-07', '長野', 'owarai'),
    4624: (1, '2026-12-09', '静岡', 'engeki'),
    4625: (1, '2027-01-31', '愛知', 'musical'),
    4626: (1, '2027-02-28', '愛知', 'musical'),
    4627: (1, '2027-03-31', '愛知', 'musical'),
    4628: (1, '2026-11-15', '愛知', 'owarai'),
    4629: (2, '2027-01-31', '新潟・富山', 'owarai'),
    4630: (1, '2026-12-13', '静岡', 'owarai'),
    4633: (1, '2026-11-15', '北海道', 'engeki'),
    4634: (2, '2026-10-31', '千葉', 'musical'),
    4635: (4, '2026-10-31', '千葉', 'musical'),
    4637: (1, '2026-11-01', '三重', 'engeki'),
    4638: (1, '2026-11-14', '愛知', 'classic'),   # +engeki は _extraGenres で別途見る
}
EXTRA = {4638: ['engeki']}

h = open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))}

ng = 0
for i, (n, last, pref, genre) in sorted(B.items()):
    e = ev.get(i)
    if not e:
        print('NG id=%d : 登録に無い' % i); ng += 1; continue
    reg_n = len(e.get('tickets') or [])
    reg_last = e.get('date')
    reg_pref = (e.get('prefecture') or '').replace('都', '').replace('府', '').replace('県', '')
    reg_genre = e.get('_genre')
    reg_extra = e.get('_extraGenres') or []
    ok_n, ok_last = (reg_n == n), (reg_last == last)
    ok_pref = (pref in reg_pref) or (reg_pref in pref)
    ok_genre = (reg_genre == genre) and (sorted(reg_extra) == sorted(EXTRA.get(i, [])))
    flag = 'OK ' if (ok_n and ok_last and ok_pref and ok_genre) else 'NG '
    if flag == 'NG ':
        ng += 1
    print('%s id=%d %-24s 枠 %d/%d %s | 千秋楽 %s/%s %s | 県 %s/%s %s | ジャンル %s%s/%s %s'
          % (flag, i, (e['name'] or '')[:24], reg_n, n, ok_n, reg_last, last, ok_last,
             reg_pref, pref, ok_pref, reg_genre, ('+' + '+'.join(reg_extra) if reg_extra else ''),
             genre, ok_genre))
print('=== 不一致 %d / %d件 ===' % (ng, len(B)))
