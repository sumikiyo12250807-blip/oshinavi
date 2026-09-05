# -*- coding: utf-8 -*-
"""merge_fix_0905.py の書き戻しを CRLF 維持に直す。"""
import io
P = 'tmp/merge_fix_0905.py'
s = io.open(P, encoding='utf-8').read()
OLD = """body = h[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]"""
NEW = """NL = '\r\n' if '\r\n' in h else '\n'
arr = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', NL)
body = h[:m.start()] + m.group(1) + arr + m.group(3) + h[m.end():]"""
assert OLD in s
io.open(P, 'w', encoding='utf-8', newline='\n').write(s.replace(OLD, NEW, 1))
print('PATCHED')
