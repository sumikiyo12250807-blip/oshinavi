# -*- coding: utf-8 -*-
"""Juice=Juice のぴあ実ページから、販売枠を1本ずつ（券種名・公演日・状態・締切）で取り出す。
パーサーが何を落としているかを、生の並びで確かめる。"""
import re, sys, html, http.client
sys.stdout.reconfigure(encoding='utf-8')


def strip(s):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or ''))).strip()


conn = http.client.HTTPSConnection('t.pia.jp', timeout=30)
conn.request('GET', '/pia/event/event.do?eventCd=2631763',
             headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
raw = conn.getresponse().read().decode('utf-8', 'replace')
txt = strip(raw)

# 「詳細はこちら」で1枠ずつ切れる並びなので、それを区切りに使う
head = txt.find('公演エリア')
body = txt[head:txt.find('アイコン説明')] if head > 0 else txt
parts = [p.strip() for p in body.split('詳細はこちら') if p.strip()]

print('=== 販売枠 %d本（生の並び）===' % len(parts))
pat = re.compile(
    r'(先行|一般発売|受付中|発売前)\s+(.*?)\s+(\d{4}/\d{1,2}/\d{1,2})\([月火水木金土日]\)\s+'
    r'(.*?)\s*\(\s*(\S+?)\s*\)\s*(抽選受付中|受付中|販売期間中|発売前|予定枚数終了)?\s*'
    r'(?:[～〜]\s*(\d{4}/\d{1,2}/\d{1,2})\([月火水木金土日]\)\s*(\d{1,2}:\d{2}))?')
n = 0
for p in parts:
    m = pat.search(p)
    if not m:
        continue
    n += 1
    kind, name, showdate, venue, pref, status, enddate, endtime = m.groups()
    print('%2d) 種別=%-6s 券種名=%s' % (n, kind, name[:44]))
    print('     公演日=%s 会場=%s(%s) 状態=%s 締切=%s %s'
          % (showdate, venue[:22], pref, status or '-', enddate or '-', endtime or ''))
print()
print('※ ぴあが返した枠 %d本' % n)
