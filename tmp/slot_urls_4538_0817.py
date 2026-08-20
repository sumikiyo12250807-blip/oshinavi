# -*- coding: utf-8 -*-
"""各販売枠のリンク先を見て、「イベント行」と「◎ODYSSEY WEB会員先行」が
別の売り場なのか、同じものの二度出しなのかを決める（推測しない）。"""
import re, sys, html, http.client
sys.stdout.reconfigure(encoding='utf-8')


def strip(s):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or ''))).strip()


conn = http.client.HTTPSConnection('t.pia.jp', timeout=30)
conn.request('GET', '/pia/event/event.do?eventCd=2631763',
             headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
raw = conn.getresponse().read().decode('utf-8', 'replace')

# 枠のカードは <li> か <div> の塊。リンク(href)と、その塊のテキストを対にする
blocks = re.split(r'(?=<a\s[^>]*href="[^"]*(?:ticketInformation|rlsCd|event\.do)[^"]*")', raw)
rows = []
for b in blocks:
    m = re.search(r'href="([^"]*(?:ticketInformation|rlsCd|event\.do)[^"]*)"', b)
    if not m:
        continue
    t = strip(b)[:170]
    if '公演' not in t and '先行' not in t:
        continue
    rows.append((m.group(1), t))

print('=== 枠とリンク先 %d件 ===' % len(rows))
seen = set()
for u, t in rows:
    key = (u, t[:60])
    if key in seen:
        continue
    seen.add(key)
    print('  URL : %s' % u[:110])
    print('  文言: %s' % t[:110])
    print()

print('=== リンク先のユニーク数 ===')
us = [u for u, _ in rows]
print('  全%d本 / ユニーク%d本' % (len(us), len(set(us))))
for u in dict.fromkeys(us):
    print('   %-100s ×%d' % (u[:100], us.count(u)))
