# -*- coding: utf-8 -*-
"""bundleページはtitleにサブジャンルが入らないので、中の個別eventCdページを1つ引いて
ぴあのカテゴリ／サブジャンルを取る（[[project_vendor_genre_autoassign]]のフォールバック）。"""
import re, sys, time, html, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

TARGETS = [
    (5155, 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670626'),
    (5158, 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670598'),
]


def get(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')


for eid, url in TARGETS:
    h = get(url)
    t = re.search(r'<title>(.*?)</title>', h, re.S)
    print('id%d bundle title = %s' % (eid, html.unescape(t.group(1)).strip() if t else '(なし)'))
    cds = re.findall(r'event\.do\?eventCd=(\d+)', h)
    seen = list(dict.fromkeys(cds))[:2]
    for cd in seen:
        time.sleep(1.5)
        h2 = get('https://t.pia.jp/pia/event/event.do?eventCd=%s' % cd)
        t2 = re.search(r'<title>(.*?)</title>', h2, re.S)
        print('   eventCd=%s title = %s' % (cd, html.unescape(t2.group(1)).strip() if t2 else '(なし)'))
    print()
    time.sleep(1.5)
