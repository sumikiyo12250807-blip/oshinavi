# -*- coding: utf-8 -*-
"""ぴあのアーティストページから、そのアーティストの全公演(eventCd)＋販売状態を総ざらいする。
状態はHTMLクラスで判定（memory: feedback_harvest_status_by_class ＝ is-active=受付中 / is-before=発売前）。

  python tmp/pia_artist_events.py E7010019
出力: tmp/pia_artist_events.txt
"""
import io, os, re, sys, time, urllib.request
import html as H

UA = {'User-Agent': 'Mozilla/5.0'}
ACD = sys.argv[1] if len(sys.argv) > 1 else 'E7010019'
OUT = os.path.join(os.path.dirname(__file__), 'pia_artist_events.txt')


def fetch(url, tries=4):
    last = None
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode('utf-8', 'replace')
        except Exception as e:
            last = e
            time.sleep(2.0 * (i + 1))
    raise last


lines = ['artistsCd=%s' % ACD, '']
seen = {}
for page in range(1, 12):
    url = 'https://t.pia.jp/pia/artist/artists.do?artistsCd=%s' % ACD
    if page > 1:
        url += '&page=%d' % page
    html = fetch(url)
    lines.append('--- page%d (%d bytes) ---' % (page, len(html)))
    if page == 1:
        ttl = re.search(r'<title>(.*?)</title>', html, re.S)
        if ttl:
            lines.append('  title: %s' % re.sub(r'\s+', ' ', H.unescape(ttl.group(1))).strip())
    # <li> 単位で切って、その中の eventCd とテキスト・状態クラスを拾う
    new = 0
    for blk in re.split(r'(?=<li)', html):
        m = re.search(r'event\.do\?[^"\']*?(event(?:Bundle)?Cd)=([A-Za-z0-9]+)', blk)
        if not m:
            continue
        cd = m.group(2)
        if cd in seen:
            continue
        txt = re.sub(r'<[^>]+>', ' ', blk)
        txt = re.sub(r'\s+', ' ', H.unescape(txt)).strip()
        st = []
        if 'is-active' in blk:
            st.append('is-active(受付中)')
        if 'is-before' in blk:
            st.append('is-before(発売前)')
        if 'is-end' in blk or 'is-finish' in blk:
            st.append('is-end(終了)')
        seen[cd] = True
        new += 1
        lines.append('  [%s] %s' % (cd, '/'.join(st) or '状態クラス無し'))
        lines.append('      %s' % txt[:300])
    lines.append('  → 新規 %d / 累計 %d' % (new, len(seen)))
    if new == 0:  # 新規URLが増えない＝終端（reference_pia_pagination_overrun）
        break
    time.sleep(2.0)

lines += ['', '=== 合計 %d 件 ===' % len(seen)]
io.open(OUT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('wrote %s (%d events)' % (OUT, len(seen)))
