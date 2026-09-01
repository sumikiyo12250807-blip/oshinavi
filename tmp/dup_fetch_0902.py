# -*- coding: utf-8 -*-
"""対象17ペアのぴあ実ページを1件ずつ開いて券種全件＋ページ見出し/主催を取る。"""
import subprocess, sys, time, io, re, os, urllib.request, html as _html

TARGETS = [
 # (tag, url)
 ('NEW6274', 'https://t.pia.jp/pia/event/event.do?eventCd=2627655'),
 ('OLD2338', 'https://t.pia.jp/pia/event/event.do?eventCd=2623354'),
 ('OLD4491', 'https://t.pia.jp/pia/event/event.do?eventCd=2628224'),
 ('OLD4509', 'https://t.pia.jp/pia/event/event.do?eventCd=2626203'),
 ('NEW6287', 'https://t.pia.jp/pia/event/event.do?eventCd=2632576'),
 ('NEW6288', 'https://t.pia.jp/pia/event/event.do?eventCd=2629110'),
 ('OLD5291', 'https://t.pia.jp/pia/event/event.do?eventCd=2607858'),
 ('OLD5291b','https://t.pia.jp/pia/event/event.do?eventCd=2626192'),
 ('NEW6290', 'https://t.pia.jp/pia/event/event.do?eventCd=2634693'),
 ('OLD695',  'https://t.pia.jp/pia/event/event.do?eventCd=2615984'),
 ('NEW6295', 'https://t.pia.jp/pia/event/event.do?eventCd=2630058'),
 ('OLD4178', 'https://t.pia.jp/pia/event/event.do?eventCd=2629081'),
 ('OLD4502', 'https://t.pia.jp/pia/event/event.do?eventCd=2632056'),
 ('OLD6080', 'https://t.pia.jp/pia/event/event.do?eventCd=2631878'),
 ('NEW6303', 'https://t.pia.jp/pia/event/event.do?eventCd=2630056'),
 ('OLD413',  'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670625'),
 ('OLD413b', 'https://t.pia.jp/pia/event/event.do?eventCd=2627160'),
 ('OLD4670', 'https://t.pia.jp/pia/event/event.do?eventCd=2628387'),
 ('NEW6304', 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670167'),
 ('OLD3551', 'https://t.pia.jp/pia/event/event.do?eventCd=2628760'),
 ('OLD3551b','https://t.pia.jp/pia/event/event.do?eventCd=2629168'),
 ('NEW6306', 'https://t.pia.jp/pia/event/event.do?eventCd=2627560'),
 ('OLD4245', 'https://t.pia.jp/pia/event/event.do?eventCd=2628948'),
 ('NEW6317', 'https://t.pia.jp/pia/event/event.do?eventCd=2633613'),
 ('OLD450',  'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2668023'),
 ('NEW6330', 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670464'),
 ('OLD2362', 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2667674'),
 ('NEW6332', 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2563199'),
 ('OLD4223', 'https://t.pia.jp/pia/event/event.do?eventCd=2632487'),
 ('NEW6342', 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670668'),
 ('OLD4843', 'https://t.pia.jp/pia/event/event.do?eventCd=2629563'),
 ('NEW6343', 'https://t.pia.jp/pia/event/event.do?eventCd=2632218'),
 ('OLD2111', 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669503'),
 ('NEW6344', 'https://t.pia.jp/pia/event/event.do?eventCd=2632255'),
 ('OLD1960', 'https://t.pia.jp/pia/event/event.do?eventCd=2545139'),
 ('OLD1961', 'https://t.pia.jp/pia/event/event.do?eventCd=2545140'),
 ('OLD4732', 'https://t.pia.jp/pia/event/event.do?eventCd=2630122'),
 ('NEW6345', 'https://t.pia.jp/pia/event/event.do?eventCd=2627800'),
 ('OLD3557', 'https://t.pia.jp/pia/event/event.do?eventCd=2622368'),
 ('OLD4207', 'https://t.pia.jp/pia/event/event.do?eventCd=2629881'),
 ('NEW6351', 'https://t.pia.jp/pia/event/event.do?eventCd=2633965'),
 ('OLD3638', 'https://t.pia.jp/pia/event/event.do?eventCd=2628113'),
 ('NEW6352', 'https://t.pia.jp/pia/event/event.do?eventCd=2630922'),
 ('OLD3406', 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669978'),
]

OUT = 'tmp/dup_pia_0902.txt'
DONE = set()
if os.path.exists(OUT):
    with io.open(OUT, encoding='utf-8') as f:
        DONE = set(re.findall(r'^##### (\S+) ', f.read(), re.M))

o = io.open(OUT, 'a', encoding='utf-8')

def txt(s):
    return _html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or ''))).strip()

def header(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        final = r.geturl(); body = r.read().decode('utf-8', 'replace')
    if 'sorry.pia' in final:
        return {'ERR': 'sorry(混雑)'}
    d = {}
    m = re.search(r'<title>(.*?)</title>', body, re.S)
    d['title'] = txt(m.group(1)) if m else ''
    m = re.search(r'<h1[^>]*>(.*?)</h1>', body, re.S)
    d['h1'] = txt(m.group(1)) if m else ''
    m = re.search(r'name="description" content="(.*?)"', body, re.S)
    d['desc'] = txt(m.group(1))[:400] if m else ''
    # 主催・企画制作などの情報テーブル
    infos = []
    for mm in re.finditer(r'<(?:dt|th)[^>]*>(.*?)</(?:dt|th)>\s*<(?:dd|td)[^>]*>(.*?)</(?:dd|td)>', body, re.S):
        k = txt(mm.group(1)); v = txt(mm.group(2))
        if re.search(r'(主催|企画|制作|問合|後援|公演に関する)', k) and v:
            infos.append(k + '=' + v[:200])
    d['info'] = ' / '.join(infos[:8])
    return d

for tag, u in TARGETS:
    if tag in DONE:
        continue
    o.write(u'##### %s %s\n' % (tag, u))
    ok = False
    for attempt in (1, 2):
        r = subprocess.run([sys.executable, 'tools/pia_tickets.py', u, '--all'],
                           capture_output=True)
        out = r.stdout.decode('utf-8', 'replace')
        err = r.stderr.decode('utf-8', 'replace')
        if 'PiaSorry' in err or '混雑' in err:
            time.sleep(20); continue
        o.write(out)
        if err.strip():
            o.write(u'  STDERR: ' + err.strip()[-300:] + u'\n')
        ok = True
        break
    if not ok:
        o.write(u'  !! 混雑ページで読めず\n')
    time.sleep(2.5)
    try:
        hd = header(u)
        for k in ('title', 'h1', 'desc', 'info'):
            if hd.get(k):
                o.write(u'  @%s: %s\n' % (k, hd[k]))
        if hd.get('ERR'):
            o.write(u'  @ERR: %s\n' % hd['ERR'])
    except Exception as e:
        o.write(u'  @header ERR: %s\n' % e)
    o.write(u'\n')
    o.flush()
    print(tag, 'done'); sys.stdout.flush()
    time.sleep(2.5)
o.close()
print('ALL DONE')
