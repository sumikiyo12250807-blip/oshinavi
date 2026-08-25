# -*- coding: utf-8 -*-
"""build_pia_entries で作り直したエントリの tickets 配列だけを index.html に当てる。
並び順・id・他フィールドは一切触らない。CRLF を壊さない（[[feedback_index_html_crlf_preserve]]）。
使い方: python tmp/apply_tickets_0825.py <built.json>
"""
import re, io, sys, json

sys.stdout.reconfigure(encoding='utf-8')
built = json.load(open(sys.argv[1], encoding='utf-8'))

path = 'index.html'
s = io.open(path, encoding='utf-8', newline='').read()
assert '\r\r\n' not in s

for e in built:
    eid = e['id']
    m = re.search(r'\n(\s*)\{\r?\n\s*"id":\s*%d,' % eid, s)
    assert m, 'id=%d が見つからない' % eid
    start = m.start() + 1
    depth = 0
    for j in range(start, len(s)):
        if s[j] == '{':
            depth += 1
        elif s[j] == '}':
            depth -= 1
            if depth == 0:
                break
    block = s[start:j + 1]

    tm = re.search(r'( *)"tickets": \[.*?\r?\n\1\],', block, re.S)
    assert tm, 'id=%d の tickets が見つからない' % eid
    ind = tm.group(1)                       # "tickets" 行のインデント
    body = json.dumps(e['tickets'], ensure_ascii=False, indent=2)
    body = '\n'.join((ind + ln) if k else ln for k, ln in enumerate(body.split('\n')))
    new = '%s"tickets": %s,' % (ind, body)
    new = new.replace('\r\n', '\n').replace('\n', '\r\n')

    old_n = len(re.findall(r'"type":', tm.group(0)))
    new_n = len(e['tickets'])
    block2 = block[:tm.start()] + new + block[tm.end():]
    s = s[:start] + block2 + s[j + 1:]
    print('id=%d tickets %d枠 → %d枠' % (eid, old_n, new_n))

assert '\r\r\n' not in s
io.open(path, 'w', encoding='utf-8', newline='').write(s)
print('CRLF', s.count('\r\n'), 'bareLF', len(re.findall(r'(?<!\r)\n', s)))
