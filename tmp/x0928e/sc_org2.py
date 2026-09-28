import sys, re, json, urllib.request, time, html as H
sys.stdout.reconfigure(encoding='utf-8')
R = 'C:/Users/user/oshinavi/tmp/x0928e/'
allb = open(R + 'sc_org.html', encoding='utf-8').read()
for p in range(2, 8):
    time.sleep(3.5)
    req = urllib.request.Request('https://livepocket.jp/p/v96ok?page=%d' % p, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36', 'Accept-Language': 'ja'})
    r = urllib.request.urlopen(req, timeout=30); b = r.read().decode('utf-8', 'replace'); print(p, r.status, len(b))
    allb += b
open(R + 'sc_org_all.html', 'w', encoding='utf-8').write(allb)
# pair each /e/ link with nearby text
for m in re.finditer(r'href="(?:https://livepocket\.jp)?/e/([^"/?#]+)"(.{0,1500}?)</a>', allb, re.S):
    t = re.sub(r'<[^>]+>', ' ', m.group(2)); t = re.sub(r'\s+', ' ', H.unescape(t)).strip()
    if 'SAKAMOTO' in t or 'BIGSTEP' in t or '心斎橋' in t:
        print(m.group(1), t[:120])
