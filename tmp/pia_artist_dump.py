# -*- coding: utf-8 -*-
"""既知のeventCdからぴあのアーティストページを辿り、そのアーティストの全公演(eventCd)を総ざらいする。
search_all.do はJS駆動で生HTMLに何も出ないため（2026-07-30実測）、
memory: feedback_harvest_name_dedup_blindspot の「artistsページでeventCd総ざらい」方式を使う。

  python tmp/pia_artist_dump.py 2621851
出力: tmp/pia_artist_dump.txt（UTF-8ファイル・コンソールに日本語を出さない）
"""
import io, os, re, sys, time, urllib.parse, urllib.request
import html as H

UA = {'User-Agent': 'Mozilla/5.0'}
OUT = os.path.join(os.path.dirname(__file__), 'pia_artist_dump.txt')
EVCD = sys.argv[1] if len(sys.argv) > 1 else '2621851'


def fetch(url, tries=4):
    last = None
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode('utf-8', 'replace')
        except Exception as e:
            last = e
            time.sleep(2.0 * (i + 1))
    raise last


lines = []
ev = fetch('https://t.pia.jp/pia/event/event.do?eventCd=%s' % EVCD)
lines.append('起点 eventCd=%s (%d bytes)' % (EVCD, len(ev)))
ttl = re.search(r'<title>(.*?)</title>', ev, re.S)
lines.append('  title: %s' % re.sub(r'\s+', ' ', H.unescape(ttl.group(1))).strip() if ttl else '  title取得不能')

# アーティストページへのリンクを全部拾う
alinks = set(re.findall(r'href="([^"]*(?:artist|artists)[^"]*)"', ev))
lines.append('')
lines.append('--- アーティスト系リンク %d 本 ---' % len(alinks))
for a in sorted(alinks):
    lines.append('  %s' % H.unescape(a))

# 同ページ内の他公演リンク（同じツアーの他会場が載ることがある）
evlinks = set(re.findall(r'href="([^"]*event\.do\?[^"]*(?:eventCd|eventBundleCd)=[^"&]+)', ev))
lines.append('')
lines.append('--- 同ページ内のイベントリンク %d 本 ---' % len(evlinks))
for a in sorted(evlinks):
    lines.append('  %s' % H.unescape(a))

io.open(OUT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('wrote %s (artistリンク%d / eventリンク%d)' % (OUT, len(alinks), len(evlinks)))
