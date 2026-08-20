# -*- coding: utf-8 -*-
"""ジャンル判断・重複判断に要る事実をぴあの実ページから取る（推測しない）。"""
import io, re, sys, json, time, html, http.client
sys.stdout.reconfigure(encoding='utf-8')

pool = {o['id']: o for o in json.load(io.open('tmp/pool_0817b.json', encoding='utf-8'))}
IDS = [4427, 4445, 4448, 4451, 4456, 4460, 4476, 4485]

conn = http.client.HTTPSConnection('t.pia.jp', timeout=30)


def strip(s):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or ''))).strip()


for i, eid in enumerate(IDS):
    u = pool[eid]['url']
    path = u.split('t.pia.jp', 1)[1]
    try:
        conn.request('GET', path, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
        r = conn.getresponse()
        body = r.read().decode('utf-8', 'replace')
        st = r.status
    except Exception as e:
        conn.close(); conn = http.client.HTTPSConnection('t.pia.jp', timeout=30)
        print('%5d FETCH FAIL %s' % (eid, e)); continue
    t = re.search(r'<title>(.*?)</title>', body, re.S)
    print('=== %d %s  (HTTP %d)' % (eid, pool[eid]['artist'][:34], st))
    print('   title :', strip(t.group(1))[:150] if t else '(なし)')
    # 公演日時・会場のブロック
    for pat, label in [(r'公演日時(.{0,200})', '公演日時'), (r'会場(.{0,120})', '会場'),
                       (r'出演(.{0,220})', '出演')]:
        m = re.search(pat, strip(body))
        if m:
            print('   %-6s: %s' % (label, m.group(1)[:190]))
    time.sleep(1.2)
