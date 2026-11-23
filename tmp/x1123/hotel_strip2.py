# -*- coding: utf-8 -*-
# 宿の帯の左右の余白をバッジ（ticket-section）にそろえる
import io, os, re, time
R = 'C:/Users/user/oshinavi/'
P = R + 'index.html'
LK = R + 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'hotel_strip2'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    t = io.open(P, encoding='utf-8', newline='').read()
    m = re.search(r'\.ticket-section\s*\{[^}]*\}', t)
    a = '.hotel-strip{display:flex;align-items:center;gap:8px;margin:10px 0 2px;'
    n = t.count(a)
    t = t.replace(a, '.hotel-strip{display:flex;align-items:center;gap:8px;margin:4px 24px 6px;')
    io.open(P, 'w', encoding='utf-8', newline='').write(t)
finally:
    os.remove(LK)
io.open(R + 'tmp/x1123/hotel_strip2.txt', 'w', encoding='utf-8').write('置換 %d\n%s\n' % (n, m.group(0) if m else 'ticket-section の CSS 見つからず'))
