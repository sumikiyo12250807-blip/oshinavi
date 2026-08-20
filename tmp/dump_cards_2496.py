# -*- coding: utf-8 -*-
"""バンドルb2666550の全ticketSalesCardを状態込みで丸ごと出す（売切も含む・取りこぼし特定用）。"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'tools')
import build_pia_entries as bpe

URL = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2666550'
html = bpe.fetch(URL)


def txt(s):
    return re.sub(r'<[^>]+>', '', s or '').strip()


cards = re.findall(r'(<[^>]*ticketSalesCard-2024__.*?)(?=<[^>]*ticketSalesCard-2024__status|\Z)', html, re.S)
# 上の分割が雑なので、statusブロック単位で拾い直す
blocks = re.split(r'(?=ticketSalesCard-2024__status is-)', html)
out = []
n = 0
for b in blocks:
    m = re.search(r'is-([\w-]+)">(.*?)(?:<br|</p>)', b, re.S)
    if not m:
        continue
    n += 1
    cls = m.group(1)
    stt = txt(m.group(2))
    # タイトル（券種名）
    title = ''
    tm = re.search(r'__ticketName[^>]*>(.*?)</', b, re.S) or re.search(r'__name[^>]*>(.*?)</', b, re.S)
    if tm:
        title = txt(tm.group(1))
    # when（販売期間）
    wm = re.search(r'<span[^>]*>(.*?)</span>', b, re.S)
    when = txt(wm.group(1)) if wm else ''
    out.append(f'[{n:>2}] is-{cls:<10} 状態={stt[:20]:<20} | {title[:40]} | 期間={when[:40]}')

open('tmp/cards_2496.txt', 'w', encoding='utf-8').write('\n'.join(out))
print(f'カード総数 {n}')
