import re, sys, time, urllib.request, html
sys.stdout.reconfigure(encoding='utf-8')
cds = {17228: 2634598, 17229: 2635073, 17230: 2635074, 17231: 2637195, 17232: 2633381, 17233: 2634442}
for i, cd in cds.items():
    u = 'https://t.pia.jp/pia/event/event.do?eventCd=%d' % cd
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0 Safari/537.36'})
        raw = urllib.request.urlopen(req, timeout=30).read()
        t = raw.decode('utf-8', 'replace')
    except Exception as e:
        print(i, cd, 'ERR', e); time.sleep(6); continue
    title = re.search(r'<title>(.*?)</title>', t, re.S)
    print('==', i, cd)
    print('TITLE:', html.unescape(title.group(1).strip()) if title else None)
    for m in sorted(set(re.findall(r'[SG]genreCd=[^"&\'\s]+', t))): print('  CD:', m)
    for m in sorted(set(re.findall(r'(?:genre|Genre)[A-Za-z_]*["\']?\s*[:=]\s*["\']([^"\']{1,60})["\']', t))): print('  GV:', m)
    bc = re.search(r'(breadcrumb|topicPath|pankuzu)[\s\S]{0,1500}', t, re.I)
    if bc:
        txt = re.sub(r'<[^>]+>', ' ', bc.group(0))
        print('  BC:', re.sub(r'\s+', ' ', html.unescape(txt))[:300])
    time.sleep(6)
