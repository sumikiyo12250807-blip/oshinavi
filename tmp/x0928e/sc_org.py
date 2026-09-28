import sys, re, json, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')
R = 'C:/Users/user/oshinavi/tmp/x0928e/'
h = open(R + 'sc_html/qw5jm.html', encoding='utf-8').read()
m = re.search(r'"organizer".*?"url":\s*"([^"]+)"', h, re.S)
u = m.group(1); print(u)
req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36', 'Accept-Language': 'ja'})
r = urllib.request.urlopen(req, timeout=30); b = r.read().decode('utf-8', 'replace')
print(r.status, len(b))
open(R + 'sc_org.html', 'w', encoding='utf-8').write(b)
ids = re.findall(r'href="(?:https://livepocket\.jp)?/e/([^"/?#]+)"', b)
print(len(ids), len(set(ids)), sorted(set(ids))[:60])
print(re.findall(r'page=\d+', b)[:10])
