# -*- coding: utf-8 -*-
# 11/16 追記用の素材：公式ページを取ってタグを外した文字を <slug>_more_<name>.txt に保存
import io, re, sys, time, urllib.request, html
D = 'C:/Users/user/oshinavi/tmp/x1116/art16/'
P = [
 ('sumidabasho_more_jungyo', 'https://www.sumo.or.jp/Jungyo/'),
 ('sumidabasho_more_timetable', 'https://www.sumo.or.jp/Jungyo/timetable/'),
]
if len(sys.argv) > 1:
    P = [tuple(a.split('=', 1)) for a in sys.argv[1:]]
for name, url in P:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'})
        raw = urllib.request.urlopen(req, timeout=40).read()
        t = raw.decode('utf-8', errors='replace')
        io.open(D + name + '.html', 'w', encoding='utf-8').write(t)
        t = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', t)
        t = re.sub(r'(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</tr>|</dt>|</dd>', '\n', t)
        t = re.sub(r'<[^>]+>', ' ', t)
        t = html.unescape(t)
        t = re.sub(r'[ \t\u3000]+', ' ', t)
        t = re.sub(r'\n\s*\n+', '\n', t)
        io.open(D + name + '.txt', 'w', encoding='utf-8').write(url + '\n\n' + t.strip())
        print(name, 'ok', len(t))
    except Exception as ex:
        print(name, 'ERR', ex)
    time.sleep(2)
