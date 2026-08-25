# -*- coding: utf-8 -*-
"""rlsInfo.do のHTMLから、絞り込みに使えるパラメータ（form input/select、リンクのクエリ）を洗い出す。"""
import re, sys, http.client, collections
sys.stdout.reconfigure(encoding='utf-8')

conn = http.client.HTTPSConnection('t.pia.jp', timeout=30)
path = '/pia/rlsInfo.do?lg=01&rlsStatus=0101&page=1'
conn.request('GET', path, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
body = conn.getresponse().read().decode('utf-8', 'replace')

print('=== form input/select name ===')
for m in re.finditer(r'<(input|select)[^>]*name="([^"]+)"[^>]*>', body):
    tag = m.group(0)
    val = re.search(r'value="([^"]*)"', tag)
    print('%-8s %-16s value=%s' % (m.group(1), m.group(2), val.group(1) if val else ''))

print()
print('=== ページ内リンクのクエリキー出現数 ===')
c = collections.Counter()
for m in re.finditer(r'href="[^"]*\?([^"]+)"', body):
    for kv in m.group(1).split('&amp;'):
        if '=' in kv:
            c[kv.split('=')[0]] += 1
for k, v in c.most_common(40):
    print('%-14s %d' % (k, v))

print()
print('=== rlsInfo.do を指す代表リンク10本 ===')
seen = set()
for m in re.finditer(r'href="([^"]*rlsInfo\.do[^"]*)"', body):
    u = m.group(1)
    if u not in seen:
        seen.add(u)
        print(u)
    if len(seen) >= 12:
        break
