d = open('index.html', 'rb').read()
print('CRLF揃い', d.count(b'\r\n') == d.count(b'\n'), 'CRCRLF', d.count(b'\r\r\n'))
