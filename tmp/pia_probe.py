# -*- coding: utf-8 -*-
"""マカロニえんぴつの全公演を取れるエンドポイントを探す（生HTMLにevent.doリンクが出るか）。
search_all.do(t.pia.jp)はJS駆動で0件、artists.do も0件だったため候補を総当たりする。"""
import re, sys, time, urllib.parse, urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
KW = 'マカロニえんぴつ'
ACD = 'E7010019'
Q = urllib.parse.quote(KW)

CANDS = [
    'https://ticket-search.pia.jp/pia/search_all.do?kw=%s' % Q,
    'https://t.pia.jp/pia/artist/rlsInfo.do?artistsCd=%s' % ACD,
    'https://t.pia.jp/pia/artist/rlsInfo.do?artistsCd=%s&lg=01' % ACD,
    'https://t.pia.jp/pia/artist/api.do?artistsCd=%s' % ACD,
    'https://t.pia.jp/pia/rlsInfo.do?kw=%s' % Q,
    'https://t.pia.jp/pia/search_dtl.do?kw=%s' % Q,
    'https://ticket-search.pia.jp/pia/search_dtl.do?kw=%s' % Q,
]

for u in CANDS:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30)
        body = r.read().decode('utf-8', 'replace')
        cds = set(re.findall(r'event\.do\?event(?:Bundle)?Cd=(\w+)', body))
        tcds = set(re.findall(r'ticketInformation\.do\?eventCd=(\w+)', body))
        print('%-3d %7d bytes  event.do:%-3d ticketInfo:%-3d  %s' % (
            r.status, len(body), len(cds), len(tcds), u))
        if cds or tcds:
            print('     eventCd例: %s' % ','.join(sorted(cds | tcds)[:12]))
    except Exception as e:
        print('ERR  %-50s %s' % (u[:50], type(e).__name__))
    time.sleep(1.5)
