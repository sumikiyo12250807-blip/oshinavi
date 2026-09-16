# -*- coding: utf-8 -*-
"""index.html の改行の指紋（bareLF / CRCRLF / 孤立CR）を数える。全部0が正常（CRLFで統一）。"""
b = open('index.html', 'rb').read()
crlf = b.count(b'\r\n')
crcrlf = b.count(b'\r\r\n')
bare_lf = b.count(b'\n') - crlf
lone_cr = b.count(b'\r') - crlf
print('CRLF=%d bareLF=%d CRCRLF=%d loneCR=%d' % (crlf, bare_lf, crcrlf, lone_cr - crcrlf))
