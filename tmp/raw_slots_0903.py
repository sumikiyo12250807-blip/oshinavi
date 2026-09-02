# -*- coding: utf-8 -*-
"""ぴあ実ページの生HTMLから「販売スケジュールの行」をそのまま抜き出して並べる。
ビルダーを介さずに券種行を数えるのが目的（ビルダーが畳んでいないかの確認）。
発売前の枠は ticketInformation リンクを持たないので、リンク数では数えられない。
"""
import re, sys, html, http.client
sys.stdout.reconfigure(encoding='utf-8')

URL = sys.argv[1]


def strip(s):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or ''))).strip()


path = URL.split('t.pia.jp', 1)[1]
conn = http.client.HTTPSConnection('t.pia.jp', timeout=40)
conn.request('GET', path, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
raw = conn.getresponse().read().decode('utf-8', 'replace')
conn.close()

print('混雑ページ:', ('大変混み合' in raw))
print('ページ消失:', ('見つかりませんでした' in raw))

# 販売スケジュールの塊＝「発売前」「受付中」「販売期間中」「予定枚数終了」「受付終了」「販売終了」を含む行
marks = ['発売前', '受付中', '販売期間中', '予定枚数終了', '抽選受付終了', '販売終了', 'まもなく抽選受付']
# li / dl / tr のブロックに切って、印を含むものだけ出す
blocks = re.split(r'(?i)(?=<li\b|<dl\b|<tr\b|<div class="[^"]*(?:ticket|release|schedule)[^"]*")', raw)
n = 0
seen = set()
for b in blocks:
    t = strip(b)
    if not t or len(t) > 400:
        continue
    if not any(m in t for m in marks):
        continue
    if t in seen:
        continue
    seen.add(t)
    n += 1
    print('  [%02d] %s' % (n, t[:220]))
print('--- 印を含むブロック %d件 ---' % n)
