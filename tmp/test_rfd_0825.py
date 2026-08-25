# -*- coding: utf-8 -*-
"""ぴあ rlsInfo.do の発売日レンジ絞り込み(rfdy/rfdm/rfdd, rtdy/rtdm/rtdd)が
本当に効くかを「総件数」で確かめる。1000件頭打ち回避の宿題の下調べ。
リクエストは数本だけ（ぴあに負荷をかけない）。
"""
import re, sys, time, http.client
sys.stdout.reconfigure(encoding='utf-8')

conn = http.client.HTTPSConnection('t.pia.jp', timeout=30)


def total(filter_str, lg='01'):
    path = '/pia/rlsInfo.do?lg=%s&%s&page=1' % (lg, filter_str)
    conn.request('GET', path, headers={'User-Agent': 'Mozilla/5.0',
                                       'Connection': 'keep-alive',
                                       'Accept-Encoding': 'identity'})
    r = conn.getresponse()
    body = r.read().decode('utf-8', 'replace')
    # 総件数の表記を探す
    cands = re.findall(r'([0-9,]+)\s*件', body)
    return r.status, cands[:5], len(body)


tests = [
    ('絞り無し(受付中)', 'rlsStatus=0101'),
    ('8月発売分', 'rlsStatus=0101&rfdy=2026&rfdm=8&rfdd=1&rtdy=2026&rtdm=8&rtdd=31'),
    ('9月発売分', 'rlsStatus=0101&rfdy=2026&rfdm=9&rfdd=1&rtdy=2026&rtdm=9&rtdd=30'),
    ('7月発売分', 'rlsStatus=0101&rfdy=2026&rfdm=7&rfdd=1&rtdy=2026&rtdm=7&rtdd=31'),
    ('発売前(絞り無し)', 'rlsIn=03'),
]
for label, f in tests:
    st, c, n = total(f)
    print('%-16s status=%s 件数候補=%s bytes=%d' % (label, st, c, n))
    time.sleep(1.5)
