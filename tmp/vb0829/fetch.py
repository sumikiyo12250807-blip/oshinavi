# -*- coding: utf-8 -*-
import json, os, re, subprocess, sys, time
sys.stdout.reconfigure(encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
BUSY = 'ただいまアクセスが集中'

def get(url, tries=6):
    fn = os.path.join(D, 'cache', re.sub(r'[^A-Za-z0-9]+', '_', url)[-120:] + '.html')
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    if os.path.exists(fn) and os.path.getsize(fn) > 20000:
        return open(fn, encoding='utf-8', errors='replace').read()
    for i in range(tries):
        p = subprocess.run(['curl', '-s', '-A', UA, '-H', 'Accept-Language: ja', url],
                           capture_output=True)
        h = p.stdout.decode('utf-8', 'replace')
        if len(h) >= 20000 and '<title>' in h:
            open(fn, 'w', encoding='utf-8').write(h)
            time.sleep(3.0)
            return h
        sys.stderr.write('RETRY %s len=%d\n' % (url, len(h)))
        time.sleep(20 * (i + 1))
    return None

if __name__ == '__main__':
    items = json.load(open(os.path.join(D, '..', 'verify_in_b_0829.json'), encoding='utf-8'))
    for it in items:
        for u in it['urls']:
            h = get(u)
            print(it['id'], u, 'OK' if h else 'FAIL', len(h or ''))
