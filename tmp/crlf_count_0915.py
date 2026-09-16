# -*- coding: utf-8 -*-
"""index.html の改行をバイト単位で数える（読むだけ・2026-09-15）。いまのファイルと HEAD を並べる。
使い方: python tmp/crlf_count_0915.py
"""
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')


def count(b, label):
    crcrlf = b.count(b'\r\r\n')
    crlf = b.count(b'\r\n') - crcrlf
    lf = b.count(b'\n') - crlf - crcrlf
    lone_cr = b.count(b'\r') - crlf - 2 * crcrlf
    print('%-8s CRLF %d / CRCRLF %d / 素のLF %d / 孤立CR %d / バイト %d' % (label, crlf, crcrlf, lf, lone_cr, len(b)))


count(open('index.html', 'rb').read(), 'いま')
count(subprocess.run(['git', 'show', 'HEAD:index.html'], capture_output=True).stdout, 'HEAD')
