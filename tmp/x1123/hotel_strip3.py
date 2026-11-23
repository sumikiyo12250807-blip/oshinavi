# -*- coding: utf-8 -*-
# 11/23 すちこ「色がかえって目立たなくなってない？　文字を大きくしたりしたほうがいいわ　横に長くするのはいい考えよ」
#   ＝宿の帯を明るい緑の塗りつぶし（元の宿ボタンの #00c887）・黒い太字 16px・光るふち。横に長い形はそのまま
import io, os, re, time
R = 'C:/Users/user/oshinavi/'
P = R + 'index.html'
LK = R + 'tmp/x1112/index.lock'
NEW = '''.hotel-strip{display:flex;align-items:center;gap:10px;margin:6px 24px 8px;padding:12px 14px;border-radius:12px;background:#00c887;border:2px solid #6fffc4;box-shadow:0 0 16px rgba(0,200,135,.55);color:#0a0a0a;text-decoration:none;font-size:16px;font-weight:700;line-height:1.4}
.hotel-strip b{font-weight:900}
.hotel-strip .hs-ico{font-size:22px}
.hotel-strip .hs-txt{flex:1;min-width:0}
.hotel-strip .hs-go{font-size:26px;color:#0a0a0a;font-weight:900}
.hotel-strip:hover{background:#19e09c}'''
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'hotel_strip3'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    t = io.open(P, encoding='utf-8', newline='').read()
    m = re.search(r'\.hotel-strip\{display:flex.*?\.hotel-strip:hover\{[^}]*\}', t, re.S)
    nl = '\r\n' if '\r\n' in m.group(0) else '\n'
    t = t[:m.start()] + NEW.replace('\n', nl) + t[m.end():]
    io.open(P, 'w', encoding='utf-8', newline='').write(t)
finally:
    os.remove(LK)
io.open(R + 'tmp/x1123/hotel_strip3.txt', 'w', encoding='utf-8').write('差し替えた %d字\n' % len(m.group(0)))
