# -*- coding: utf-8 -*-
"""音楽の発売前(rlsIn=03)が62ページ中39ページで打ち切られる原因を見る。
終端判定＝「そのページのURL並びが前ページと完全に同一」が2回連続。
実際に 36〜44ページを取って、並びと件数を並べて確かめる。"""
import re, sys, time, html, http.client
sys.stdout.reconfigure(encoding='utf-8')

conn = http.client.HTTPSConnection('t.pia.jp', timeout=30)


def fetch(page):
    path = '/pia/rlsInfo.do?lg=01&rlsIn=03&page=%d' % page
    conn.request('GET', path, headers={'User-Agent': 'Mozilla/5.0',
                                       'Connection': 'keep-alive',
                                       'Accept-Encoding': 'identity'})
    r = conn.getresponse()
    return r.read().decode('utf-8', 'replace')


def urls(h):
    return re.findall(r'<a href="([^"]*event\.do\?event(?:Bundle)?Cd=\w+)"', h)


prev = None
for p in range(36, 45):
    h = fetch(p)
    u = urls(h)
    m = re.search(r'全([0-9,]+)件中\s*([0-9,]+)[^0-9]+([0-9,]+)件', h)
    rng = m.group(0) if m else '(件数表記なし)'
    same = (u == prev)
    print('page %2d  リンク%3d本  前ページと同一=%s  %s' % (p, len(u), same, rng))
    prev = u
    time.sleep(0.8)
