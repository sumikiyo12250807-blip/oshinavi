# -*- coding: utf-8 -*-
"""4448/4476 が「同じ公演の重複」か「同日2回公演」かを実ページの公演日時で確定させる。
あわせて 4427 サックス侍の公式でジャンルの手がかりを取る。"""
import re, sys, time, html, http.client, urllib.request
sys.stdout.reconfigure(encoding='utf-8')


def strip(s):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or ''))).strip()


conn = http.client.HTTPSConnection('t.pia.jp', timeout=30)
for cd, eid in [('2629200', 4448), ('2629201', 4476), ('2628196', 4450), ('2629609', 4477)]:
    conn.request('GET', '/pia/event/event.do?eventCd=%s' % cd,
                 headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
    body = conn.getresponse().read().decode('utf-8', 'replace')
    txt = strip(body)
    print('=== id%d eventCd=%s' % (eid, cd))
    for pat in [r'(20\d\d年\s*\d+月\s*\d+日[^ ]{0,30}\s*\d{1,2}:\d{2})',
                r'(\d{4}/\d{1,2}/\d{1,2}[^ ]{0,12}\s*\d{1,2}:\d{2})',
                r'開演\s*(\d{1,2}:\d{2})', r'開場\s*(\d{1,2}:\d{2})']:
        hits = re.findall(pat, txt)
        if hits:
            print('   ', pat[:22], '→', list(dict.fromkeys(hits))[:6])
    m = re.search(r'公演期間(.{0,90})', txt)
    if m:
        print('    公演期間:', m.group(1)[:90])
    time.sleep(1.2)

print()
print('=== サックス侍 公式 ===')
try:
    req = urllib.request.Request('https://www.saxsamurai.nagoya/live-schedule',
                                 headers={'User-Agent': 'Mozilla/5.0'})
    b = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
    t = re.search(r'<title>(.*?)</title>', b, re.S)
    print('  title:', strip(t.group(1))[:120] if t else '(なし)')
    print('  本文:', strip(b)[:400])
except Exception as e:
    print('  FAIL', e)
