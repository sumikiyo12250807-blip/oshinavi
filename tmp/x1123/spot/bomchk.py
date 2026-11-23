# -*- coding: utf-8 -*-
import io
b = open('C:/Users/user/oshinavi/.claude/hooks/shift_guard.ps1', 'rb').read()
io.open('C:/Users/user/oshinavi/tmp/x1123/spot/bomchk.txt', 'w', encoding='utf-8').write(
    'BOM %s / CRLF %d / 素のLF %d\n' % (b[:3] == b'\xef\xbb\xbf', b.count(b'\r\n'), b.count(b'\n') - b.count(b'\r\n')))
