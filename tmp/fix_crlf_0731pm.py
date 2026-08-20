# -*- coding: utf-8 -*-
"""index.html の改行をCRLFに戻す。
原因＝newline='' で読み書きしたのに EVENTS 部分を json.dumps で作り直したため、
その部分だけ LF になった（[[feedback_index_html_crlf_preserve]]）。
復旧＝いったん全部 LF に畳んでから CRLF に戻す。バックアップと指紋照合する。"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

p = 'index.html'
b = open(p, 'rb').read()
print('before: CRLF=%d 単独LF=%d' % (b.count(b'\r\n'), b.count(b'\n') - b.count(b'\r\n')))
flat = b.replace(b'\r\n', b'\n')
assert flat.count(b'\r') == 0, '孤立CRが残っている'
fixed = flat.replace(b'\n', b'\r\n')
print('after : CRLF=%d 単独LF=%d' % (fixed.count(b'\r\n'), fixed.count(b'\n') - fixed.count(b'\r\n')))
open(p, 'wb').write(fixed)

# 指紋照合＝並び順ロジックのブロックがバックアップと一致するか
bak = open('index.html.bak_0731pm_draftfix', 'rb').read()
print('backup: CRLF=%d 単独LF=%d' % (bak.count(b'\r\n'), bak.count(b'\n') - bak.count(b'\r\n')))
ok = True
for key in ('saleStartPending', 'function sortEvents', '.sort(', 'NEW_ORDER'):
    a = [x for x in re.findall(re.escape(key.encode()) + rb'.{0,220}', bak, re.S)]
    c = [x for x in re.findall(re.escape(key.encode()) + rb'.{0,220}', fixed, re.S)]
    same = (a == c)
    ok &= same
    print('  指紋 %-22s 出現 %d/%d 一致=%s' % (key, len(a), len(c), same))
print('全ブロック一致 =', ok)
