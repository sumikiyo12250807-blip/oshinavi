# TIGETの各イベントページで「TikTok」の前後の文を抜き出す（TikTokerのイベントかどうかを見るため）
import re, sys, time, urllib.request, html as H
sys.stdout.reconfigure(encoding='utf-8')
IDS = ['498607', '520477', '523992', '523784', '522705', '522174']
EXTRA = sys.argv[1:]
UA = {'User-Agent': 'Mozilla/5.0'}
for i in IDS + EXTRA:
    s = urllib.request.urlopen(urllib.request.Request('https://tiget.net/events/' + i, headers=UA), timeout=30).read().decode('utf-8', 'replace')
    t = H.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)))
    title = re.search(r'<title>(.*?)</title>', s, re.S)
    hits = [t[max(0, m.start() - 60):m.end() + 60] for m in re.finditer(r'tik\s*tok|ティックトック', t, re.I)][:2]
    print('■', i, H.unescape(title.group(1)).strip()[:70] if title else '')
    for h in hits:
        print('   …', h)
    time.sleep(0.8)
