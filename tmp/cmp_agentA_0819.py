# -*- coding: utf-8 -*-
"""検証エージェントA（13件）が実ページからゼロ導出した値と、index.html の登録値を機械照合する。
エージェント側の値はこのファイルに転記（人の目で読んで判断しない＝ASCIIブールで突合する）。
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

# id: (枠数, 千秋楽, 都道府県, ジャンル)
A = {
    4591: (1, '2026-12-20', '沖縄', 'jpop'),
    4601: (1, '2026-11-14', '宮城', 'jpop'),
    4603: (2, '2026-10-14', '大阪', 'jpop'),
    4609: (1, '2026-11-28', '山口', 'jpop'),
    4610: (1, '2026-10-18', '神奈川', 'jpop'),
    4611: (1, '2026-11-29', '東京', 'jazz'),
    4612: (1, '2026-10-17', '大阪', 'jpop'),
    4613: (1, '2026-12-04', '東京', 'dento'),
    4615: (1, '2026-12-19', '愛知', 'musical'),
    4616: (1, '2026-12-05', '福岡', 'engeki'),
    4619: (1, '2026-11-20', '富山', 'dento'),
    4620: (1, '2026-12-10', '東京', 'owarai'),
    4622: (1, '2026-11-06', '東京', 'engeki'),
}

h = open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))}

ng = 0
for i, (n, last, pref, genre) in sorted(A.items()):
    e = ev.get(i)
    if not e:
        print('NG id=%d : 登録に無い' % i); ng += 1; continue
    reg_n = len(e.get('tickets') or [])
    reg_last = e.get('date')
    reg_pref = (e.get('prefecture') or '').replace('都', '').replace('府', '').replace('県', '')
    reg_genre = e.get('_genre')
    ok_n, ok_last = (reg_n == n), (reg_last == last)
    ok_pref = (pref in reg_pref) or (reg_pref in pref)
    ok_genre = (reg_genre == genre)
    flag = 'OK ' if (ok_n and ok_last and ok_pref and ok_genre) else 'NG '
    if flag == 'NG ':
        ng += 1
    print('%s id=%d %-26s 枠 %d/%d %s | 千秋楽 %s/%s %s | 県 %s/%s %s | ジャンル %s/%s %s'
          % (flag, i, (e['name'] or '')[:26], reg_n, n, ok_n, reg_last, last, ok_last,
             reg_pref, pref, ok_pref, reg_genre, genre, ok_genre))
print('=== 不一致 %d / %d件 ===' % (ng, len(A)))
