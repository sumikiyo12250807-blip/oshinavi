# -*- coding: utf-8 -*-
"""index.html の改行を CRLF に戻す。
tmp/assign_hold4_0819.py を newline='' で書いたせいで、json.dumps が作った EVENTS 部分だけ LF になった
（[[feedback_index_html_crlf_preserve]] の既知の罠。newline='' でも json.dumps の中身は LF）。
中身（EVENTS の内容）は一切変えず、改行コードだけ揃える。
"""
import re, json, sys, hashlib, shutil
sys.stdout.reconfigure(encoding='utf-8')

raw = open('index.html', 'rb').read()
print('前 : CRLF %d / LF単独 %d' % (raw.count(b'\r\n'), raw.count(b'\n') - raw.count(b'\r\n')))

fixed = raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')

# 中身が変わっていないことを EVENTS の JSON で検算する
def events_of(b):
    t = b.decode('utf-8').replace('\r\n', '\n')
    return json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', t, re.S).group(2))

a, b = events_of(raw), events_of(fixed)
ha = hashlib.md5(json.dumps(a, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
hb = hashlib.md5(json.dumps(b, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
print('EVENTS 件数 %d / %d  ハッシュ %s / %s  一致=%s' % (len(a), len(b), ha[:8], hb[:8], ha == hb))
if ha != hb or len(a) != len(b):
    print('!! 中身が変わっている。書き戻さない')
    sys.exit(1)

shutil.copyfile('index.html', 'index.html.bak_0819_precrlf')
open('index.html', 'wb').write(fixed)
raw2 = open('index.html', 'rb').read()
print('後 : CRLF %d / LF単独 %d' % (raw2.count(b'\r\n'), raw2.count(b'\n') - raw2.count(b'\r\n')))
