# -*- coding: utf-8 -*-
"""ぴあ受付中（rlsStatus=0101）を「1本1,000件未満」に割って presale_harvest.py で回す（2026-09-22）。
ぴあの一覧は1本の検索で先頭約1,000件までしか返さない（memory reference_pia_pagination_overrun）。
割り方＝sg（下位ジャンル）。1,000件を超える sg は pf（都道府県 01〜47）でさらに割る。
  python tmp/x0922/pia_onsale_split.py 01            # 音楽
出力＝tmp/x0922/onsale_<lg>/<sg>_<pf>.json（presale_harvest の形）。まとめは make_cands.py に glob で渡す。
ぴあは叩きすぎると429＝直列＋間を置く。
"""
import os, re, subprocess, sys, time, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
LG = sys.argv[1] if len(sys.argv) > 1 else '01'
OUT = 'tmp/x0922/onsale_%s' % LG
os.makedirs(OUT, exist_ok=True)


def count(q):
    u = 'https://t.pia.jp/pia/rlsInfo.do?lg=%s&rlsStatus=0101&page=1%s' % (LG, q)
    h = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf-8', 'replace')
    m = re.search(r'([0-9,]+)\s*件', h)
    time.sleep(1.5)
    return int(m.group(1).replace(',', '')) if m else -1


total = count('')
print('lg=%s 受付中 総%d件' % (LG, total))
jobs = []
for n in range(1, 31):
    sg = '%s00%03d' % (LG, 100 + n)   # 音楽なら 0100101〜
    c = count('&sg=' + sg)
    if c <= 0 or c == total:
        continue                      # 無い番号＝絞り込みが外れて全件が返る
    if c < 1000:
        jobs.append((sg, '', c))
    else:
        for p in range(1, 48):
            cp = count('&sg=%s&pf=%02d' % (sg, p))
            if cp > 0:
                jobs.append((sg, '%02d' % p, cp))
            if cp >= 1000:
                print('⚠️ %s pf=%02d がまだ1,000件以上＝この県は取り切れない' % (sg, p))
print('回す本数 %d／件数の合計 %d（総%d件）' % (len(jobs), sum(j[2] for j in jobs), total))
for sg, pf, c in jobs:
    f = '%s/%s_%s.json' % (OUT, sg, pf or 'all')
    if os.path.exists(f):
        continue
    flt = 'rlsStatus=0101&sg=%s%s' % (sg, ('&pf=' + pf) if pf else '')
    r = subprocess.run([sys.executable, '-u', 'tools/presale_harvest.py', LG, f, flt],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    tail = [x for x in r.stdout.splitlines() if 'NOT in DB' in x or 'parsed items' in x]
    print('%s pf=%s 件数%d | %s' % (sg, pf or '-', c, ' / '.join(tail)))
    time.sleep(5)
print('ALL DONE')
