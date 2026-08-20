# -*- coding: utf-8 -*-
"""Juice=Juice のぴあ実ページから、券種の生の名前を洗い出す。
パーサーが「先行」に潰しているのか、ぴあ側も「先行」としか書いていないのかを切り分ける。"""
import re, sys, html, http.client
sys.stdout.reconfigure(encoding='utf-8')


def strip(s):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or ''))).strip()


conn = http.client.HTTPSConnection('t.pia.jp', timeout=30)
conn.request('GET', '/pia/event/event.do?eventCd=2631763',
             headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
raw = conn.getresponse().read().decode('utf-8', 'replace')
print('len', len(raw))

# 販売枠のブロックらしきものを列挙
print()
print('=== 「先行」「発売」を含む短い断片 ===')
txt = strip(raw)
seen = []
for m in re.finditer(r'[^ ]{0,40}(先行|プレリザーブ|プリセール|一般発売|抽選|受付)[^ ]{0,40}', txt):
    s = m.group(0).strip()
    if s and s not in seen:
        seen.append(s)
for s in seen[:40]:
    print('  ', s[:90])

print()
print('=== HTMLの券種っぽいクラス/見出し ===')
for pat in [r'class="[^"]*(?:rls|kenshu|ticket|sale)[^"]*"[^>]*>\s*([^<]{2,60})',
            r'<h[34][^>]*>\s*([^<]{2,60})\s*</h[34]>',
            r'<dt[^>]*>\s*([^<]{2,60})\s*</dt>']:
    hits = [strip(x) for x in re.findall(pat, raw)]
    hits = [h for h in dict.fromkeys(hits) if h]
    if hits:
        print(' pattern:', pat[:40])
        for h in hits[:25]:
            print('    ', h[:80])
