# -*- coding: utf-8 -*-
"""関東 J-POP の都道府県（pf）割りが効いているか1本で確かめる（2026-09-14 夜・plan.md の宿題）。
朝の総ざらいで、関東 J-POP・ROCK のどの県も「総1,300〜1,600・取得720前後」でほぼ同じ数だった
＝pf が無視されて関東全体を毎回読んでいる疑い。
同じ絞り込み（受付中・J-POP・ROCK・関東）に pf を 無し／13東京／14神奈川／08茨城 と変えて、
①総件数 ②1ページ目の売り場の番号 ③1ページ目に出る県名の数 を並べる。
pf が効いていれば、神奈川と茨城の1ページ目は東京と別物で、県名もその県に偏るはず。
ぴあは1本ずつ・間を空けて叩く（4ページだけ）。
使い方: python tmp/pf_check_0914.py
"""
import http.client
import re
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
BASE = '/pia/rlsInfo.do?lg=01&rlsStatus=0101&sg=0100102&rg=01'
PREFS = ['東京都', '神奈川県', '千葉県', '埼玉県', '茨城県', '栃木県', '群馬県', '山梨県', '新潟県', '長野県']


def get(path):
    c = http.client.HTTPSConnection('t.pia.jp', timeout=30)
    c.request('GET', path, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
    r = c.getresponse()
    b = r.read().decode('utf-8', 'replace')
    c.close()
    return r.status, b


rows = {}
for pf in ['', '13', '14', '08']:
    path = BASE + ('&pf=%s' % pf if pf else '') + '&page=1'
    st, b = get(path)
    m = re.search(r'全([0-9,]+)件中', b)
    codes = re.findall(r'(eventBundleCd=b?\d+|eventCd=\d+)', b)
    seen = []
    for c in codes:
        if c not in seen:
            seen.append(c)
    counts = {p: b.count(p) for p in PREFS if b.count(p)}
    rows[pf] = seen
    print('pf=%-3s 状態%s 総件数=%s ｜1ページ目の売り場 %d件 ｜県名 %s' % (
        pf or '無し', st, m.group(1) if m else '取れず', len(seen),
        '・'.join('%s%d' % (p[:-1] if p.endswith(('県', '都')) else p, n) for p, n in counts.items()) or 'なし'))
    time.sleep(1.5)

print()
for a, b in [('13', '14'), ('13', '08'), ('', '13')]:
    sa, sb = set(rows[a]), set(rows[b])
    print('pf=%s と pf=%s の1ページ目＝同じ売り場 %d／片方だけ %d・%d' % (
        a or '無し', b or '無し', len(sa & sb), len(sa - sb), len(sb - sa)))
