# -*- coding: utf-8 -*-
"""429明けの小さなバッチ。①4448/4476の公演時刻（同日同会場のバッジを見分けるため
[[feedback_same_day_show_time_badge]]）②落ちた4505の素性確認。ぴあは3リクエストだけ。"""
import re, sys, time, html, http.client
sys.stdout.reconfigure(encoding='utf-8')


def strip(s):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or ''))).strip()


conn = http.client.HTTPSConnection('t.pia.jp', timeout=30)
for lab, cd in [('4448', '2629200'), ('4476', '2629201'), ('4505', '2623842')]:
    conn.request('GET', '/pia/event/event.do?eventCd=%s' % cd,
                 headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
    r = conn.getresponse()
    raw = r.read().decode('utf-8', 'replace')
    txt = strip(raw)
    print('=== id%s eventCd=%s HTTP %d len=%d' % (lab, cd, r.status, len(raw)))
    if 'sorry.pia.jp' in raw or len(raw) < 3000:
        print('    まだ sorry ページ／中身が薄い')
    # 開演/開場/公演時刻らしきものを全部出す
    for pat, name in [(r'開場\s*([0-9]{1,2}[:：][0-9]{2})', '開場'),
                      (r'開演\s*([0-9]{1,2}[:：][0-9]{2})', '開演'),
                      (r'(\d{1,2}[:：]\d{2})\s*開演', '開演(逆順)'),
                      (r'第?([12１２])\s*部', '部')]:
        h = re.findall(pat, txt)
        if h:
            print('    %-9s %s' % (name, list(dict.fromkeys(h))[:8]))
    m = re.search(r'公演期間(.{0,70})', txt)
    if m:
        print('    公演期間 %s' % m.group(1).strip()[:70])
    # 券種名（1部/2部の区別が券種側に出ていることがある）
    ks = re.findall(r'"(?:ticketName|kenshuName)"\s*:\s*"([^"]{2,40})"', raw)
    if ks:
        print('    券種:', list(dict.fromkeys(ks))[:8])
    for m2 in re.finditer(r'class="[^"]*kenshu[^"]*"[^>]*>(.{0,60})', raw):
        s = strip(m2.group(1))
        if s:
            print('    券種欄:', s[:60])
    time.sleep(2.0)
