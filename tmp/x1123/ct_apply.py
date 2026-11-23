# -*- coding: utf-8 -*-
# 鍵の中で index.html のクリック計測を新しい形に差し替え → 差し替わったか・CRLF が崩れていないか
import io, os, sys, time
R = 'C:/Users/user/oshinavi/'
os.chdir(R)
sys.path.insert(0, R + 'tools')
import click_track as CT
LK = R + 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'ct_apply'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    r = CT.inject_index('index.html')
finally:
    os.remove(LK)
b = open('index.html', 'rb').read()
t = b.decode('utf-8')
io.open(R + 'tmp/x1123/ct_apply.txt', 'w', encoding='utf-8').write(
    '差し替え=%s 7net入り=%s ticketdive入り=%s CRCRLF=%d 素のLF=%d\n' % (r, "'7net'" in t, 'ticketdive' in t[:5000], b.count(b'\r\r\n'), b.count(b'\n') - b.count(b'\r\n')))
