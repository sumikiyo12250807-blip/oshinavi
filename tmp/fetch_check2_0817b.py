# -*- coding: utf-8 -*-
"""エージェントと判定が割れた件・見落とし重複を、自分で実ページから確かめる
（[[feedback_no_speculation]]／他エージェントの結論も鵜呑みにしない）。"""
import re, sys, time, html, http.client
sys.stdout.reconfigure(encoding='utf-8')

TARGET = [(4456, '2629366'), (4485, '2626268'), (4479, '2626269'), (4480, '2626270')]


def strip(s):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or ''))).strip()


import io, json
pool = {o['id']: o for o in json.load(io.open('tmp/pool_0817b.json', encoding='utf-8'))}
conn = http.client.HTTPSConnection('t.pia.jp', timeout=30)
for eid in (4456, 4485, 4479, 4480):
    u = pool[eid]['url']
    conn.request('GET', u.split('t.pia.jp', 1)[1],
                 headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
    txt = strip(conn.getresponse().read().decode('utf-8', 'replace'))
    print('=== %d %s' % (eid, pool[eid]['artist'][:40]))
    print('    url:', u)
    for pat, lab in [(r'公演期間(.{0,80})', '公演期間'), (r'［出演］(.{0,160})', '出演'),
                     (r'［ゲスト］(.{0,120})', 'ゲスト'), (r'［共演］(.{0,120})', '共演'),
                     (r'注意事項(.{0,140})', '注意')]:
        m = re.search(pat, txt)
        if m:
            print('    %-6s %s' % (lab, m.group(1).strip()[:150]))
    t = re.search(r'([^|]{0,80})\| チケットぴあ\[(.{0,40})の', txt)
    if t:
        print('    ぴあ表記名/カテゴリ:', t.group(1).strip()[:60], '/', t.group(2))
    time.sleep(1.5)
