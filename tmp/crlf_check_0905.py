# -*- coding: utf-8 -*-
import io, sys
h = io.open('index.html', encoding='utf-8', newline='').read()
print('CRLF=%d LF_only=%d' % (h.count('\r\n'), h.count('\n') - h.count('\r\n')))
