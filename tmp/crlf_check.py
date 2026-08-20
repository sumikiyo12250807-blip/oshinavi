# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
b = open(sys.argv[1] if len(sys.argv) > 1 else 'index.html', 'rb').read()
print('CRLF', b.count(b'\r\n'), ' 単独LF', b.count(b'\n') - b.count(b'\r\n'), ' size', len(b))
