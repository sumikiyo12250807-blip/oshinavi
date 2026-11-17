# -*- coding: utf-8 -*-
# 11/17 記事3本の材料：売り場・報道のページを取ってタグを外した文字を保存（引用は生HTMLと機械で照合するため）
import io, re, sys, time, urllib.request, html
D = 'C:/Users/user/oshinavi/tmp/x1117/art17/'
P = [
 ('minamikousetsu_eplus', 'https://eplus.jp/sf/detail/4603880001'),
 ('minamikousetsu_eplus_tokyo', 'https://eplus.jp/sf/detail/4603880001-P0030003P021001'),
 ('danseiburanko_fany', 'https://ticket.fany.lol/event/detail/22805'),
 ('hikawakiyoshi_eplus_kyusyu', 'https://eplus.jp/sf/detail/4620100001'),
 ('hikawakiyoshi_eplus_tour', 'https://eplus.jp/sf/detail/0036090001'),
 ('hikawakiyoshi_realsound', 'https://realsound.jp/2026/09/post-2518509.html'),
 ('minamikousetsu_official', 'https://www.kosetsu.com/'),
 ('minamikousetsu_schedule', 'https://www.kosetsu.com/schedule/'),
 ('minamikousetsu_hitachinaka', 'https://hitachinaka-culturehall.jp/archives/ticket/%E5%8D%97%E3%81%93%E3%81%86%E3%81%9B%E3%81%A4%E3%80%80%E3%82%B3%E3%83%B3%E3%82%B5%E3%83%BC%E3%83%88%E3%83%84%E3%82%A2%E3%83%BC2027%EF%BD%9E%E5%90%9B%E3%81%A8%E5%83%95%E3%81%AE%E3%81%86%E3%81%9F'),
 ('minamikousetsu_niigata', 'https://www.niigata-kenminkaikan.jp/event/20343/'),
 ('danseiburanko_official', 'https://dansei-blanco.com/'),
 ('danseiburanko_prtimes', 'https://prtimes.jp/main/html/rd/p/000005465.000029501.html'),
 ('danseiburanko_fanymag', 'https://magazine.fany.lol/295312/'),
]
if len(sys.argv) > 1:
    P = [p for p in P if p[0] in sys.argv[1:]]
log = io.open(D + 'fetch.txt', 'a', encoding='utf-8')
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
        log.write('%s ok %d\n' % (name, len(t)))
    except Exception as ex:
        log.write('%s ERR %s\n' % (name, ex))
    time.sleep(3)
