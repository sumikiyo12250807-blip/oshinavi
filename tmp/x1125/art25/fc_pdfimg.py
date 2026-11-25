import re
b = open(r'C:\Users\user\.claude\projects\C--Users-user-oshinavi\187b3f7d-f8a4-4c61-87b1-b363aacd839c\tool-results\webfetch-1795570256551-b56hsu.pdf', 'rb').read()
n = 0
i = 0
while True:
    s = b.find(b'\xff\xd8\xff', i)
    if s < 0:
        break
    e = b.find(b'\xff\xd9', s)
    # find the last EOI before 'endstream'
    es = b.find(b'endstream', s)
    if es > 0:
        e = b.rfind(b'\xff\xd9', s, es)
    if e < 0:
        break
    n += 1
    open(r'C:\Users\user\AppData\Local\Temp\claude\ac08c5b2b244d5f8\187b3f7d-f8a4-4c61-87b1-b363aacd839c\scratchpad\toki_%d.jpg' % n, 'wb').write(b[s:e + 2])
    print(n, e + 2 - s)
    i = e + 2
