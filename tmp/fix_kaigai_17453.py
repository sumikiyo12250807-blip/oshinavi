# -*- coding: utf-8 -*-
"""id17453「마쏘 팬미팅 IN 서울」の prefecture を「海外」にする。
会場が BBQ치킨 역삼스타점（ソウル）＝日本の県ではないので、エリアの絞り込み（kaigai）に入れる。
[[feedback_kaigai_is_area]]＝「海外」はジャンルでなくエリア。
🚨index.html は CRLF。newline='' で読み書きしないと全行LF化して sort_guard が誤ブロックする。
"""
import io, json, re, sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

PATH = 'index.html'
src = io.open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
assert m, 'EVENTS配列が無い'
ev = json.loads(m.group(2))
nl = '\r\n' if '\r\n' in src else '\n'

hit = 0
for e in ev:
    if e.get('id') == 17453:
        print('before: prefecture=%r venue=%r' % (e.get('prefecture'), e.get('venue')))
        e['prefecture'] = '海外'
        hit += 1
assert hit == 1, 'id17453 が見つからない（%d件）' % hit

new = json.dumps(ev, ensure_ascii=False, indent=2).replace('\n', nl)
out = src[:m.start()] + m.group(1) + new + m.group(3) + src[m.end():]
io.open(PATH, 'w', encoding='utf-8', newline='').write(out)
print('id17453 の prefecture を「海外」にした')
