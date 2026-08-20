# -*- coding: utf-8 -*-
"""PowerShellのリダイレクトが付けたUTF-8 BOMを除去して書き戻す"""
import io, json, sys

p = sys.argv[1]
data = io.open(p, 'rb').read()
if data.startswith(b'\xef\xbb\xbf'):
    data = data[3:]
    io.open(p, 'wb').write(data)
    print('BOM除去: %s' % p)
else:
    print('BOMなし: %s' % p)
arr = json.loads(data.decode('utf-8'))
print('エントリ %d件 / id %s..%s' % (len(arr), arr[0]['id'], arr[-1]['id']))
