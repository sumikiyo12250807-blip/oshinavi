# -*- coding: utf-8 -*-
# 公式ページを取ってタグを外した文字を保存（引用は生HTMLから機械で照合するため）
import io, re, sys, time, urllib.request, html
D = 'C:/Users/user/oshinavi/tmp/x1116/art16/'
P = [
 ('freedomofchoice_eplus0131', 'https://eplus.jp/sf/detail/4623680003-P0030002P021012'),
 ('takahashiyu_special', 'https://fc.takahashiyu.com/feature/free_style_stroke2'),
 ('freedomofchoice_cubetheater', 'https://www.cubeinc.co.jp/archives/theater/freedomofchoice'),
 ('takahashiyu_pia', 'https://t.pia.jp/pia/event/event.do?eventCd=2637991'),
 ('sumidabasho_pia', 'https://t.pia.jp/pia/event/event.do?eventCd=2643420'),
 ('takahashiyu_official', 'https://www.takahashiyu.com/news/livetour2027%e3%80%8cfree-style-stroke-2%e3%80%8dinfo/'),
 ('sumidabasho_official', 'https://oosumo.com/sumida/'),
 ('freedomofchoice_toho', 'https://www.tohostage.com/freedom_of_choice/'),
 ('freedomofchoice_hakataza', 'https://www.hakataza.co.jp/lineup/168'),
 ('freedomofchoice_cube', 'https://www.cubeinc.co.jp/archives/16522'),
 ('freedomofchoice_astage', 'https://www.astage-ent.com/stage-musical/s303510.html'),
]
if len(sys.argv) > 1:
    P = [p for p in P if p[0] in sys.argv[1:]]
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
