# -*- coding: utf-8 -*-
"""index.html の改行がCRLF統一されているか（LF単独の混入検出）"""
data = open('index.html', 'rb').read()
crlf = data.count(b'\r\n')
lf = data.count(b'\n')
lone_lf = lf - crlf
print('CRLF=%d  LF総数=%d  LF単独=%d' % (crlf, lf, lone_lf))
if lone_lf:
    idx = 0
    shown = 0
    while shown < 5:
        idx = data.find(b'\n', idx)
        if idx < 0:
            break
        if idx == 0 or data[idx-1:idx] != b'\r':
            line = data[:idx].count(b'\n') + 1
            print('  LF単独 行%d: %r' % (line, data[max(0, idx-90):idx][-90:]))
            shown += 1
        idx += 1
print('判定: %s' % ('OK（CRLF統一）' if lone_lf == 0 else 'NG（LF混在）'))
