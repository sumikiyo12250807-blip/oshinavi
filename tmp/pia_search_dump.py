# -*- coding: utf-8 -*-
"""ぴあの検索結果ページから公演カードを機械抽出する（WebFetchの要約で枠を落とさないため）。
  python tmp/pia_search_dump.py マカロニえんぴつ
出力: tmp/pia_search_<kw>.txt（UTF-8・コンソールに日本語を出さない＝化け読み防止）
"""
import io, json, os, re, sys, time, urllib.parse, urllib.request
import html as H

UA = {'User-Agent': 'Mozilla/5.0'}
KW = sys.argv[1] if len(sys.argv) > 1 else 'マカロニえんぴつ'
OUT = os.path.join(os.path.dirname(__file__), 'pia_search_dump.txt')


def fetch(url, tries=4):
    last = None
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode('utf-8', 'replace')
        except Exception as e:
            last = e
            time.sleep(2.0 * (i + 1))
    raise last


lines = ['検索語: %s' % KW, '']
seen = {}
for page in range(1, 8):
    url = 'https://t.pia.jp/pia/search_all.do?kw=%s' % urllib.parse.quote(KW)
    if page > 1:
        url += '&page=%d' % page
    html = fetch(url)
    lines.append('--- page%d 取得 %d bytes ---' % (page, len(html)))
    # イベントカード（eventCd / eventBundleCd）を出現順に拾う
    cards = re.findall(r'href="(/pia/event/event\.do\?[^"]*(?:eventCd|eventBundleCd)=[^"]+)"(.*?)(?=<a\s|</li>|</div>\s*</div>)', html, re.S)
    new = 0
    for href, seg in cards:
        key = re.search(r'(event(?:Bundle)?Cd)=([A-Za-z0-9]+)', href)
        if not key:
            continue
        cd = key.group(2)
        txt = re.sub(r'<[^>]+>', ' ', seg)
        txt = re.sub(r'\s+', ' ', H.unescape(txt)).strip()
        if cd in seen:
            continue
        seen[cd] = True
        new += 1
        lines.append('  [%s] https://t.pia.jp%s' % (cd, href.replace('&amp;', '&')))
        lines.append('      %s' % txt[:400])
    lines.append('  → 新規 %d 件 / 累計 %d 件' % (new, len(seen)))
    if new == 0:  # 新規URLが増えない＝終端（memory: reference_pia_pagination_overrun）
        break
    time.sleep(2.0)

lines.append('')
lines.append('=== 合計 %d 件のイベントURL ===' % len(seen))
io.open(OUT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('wrote %s (%d events)' % (OUT, len(seen)))
