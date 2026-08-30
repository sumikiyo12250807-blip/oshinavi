# -*- coding: utf-8 -*-
import re, io, os

CACHE = 'C:/Users/user/oshinavi/tmp/_agentB_cache'
OUT = 'C:/Users/user/oshinavi/tmp/_agentB_detail.txt'
ids = ['5998', '5999', '6008', '6012', '6015', '5997', '6013', '6010', '6005', '6021']
out = io.open(OUT, 'w', encoding='utf-8')


def strip(x):
    x = re.sub(r'(?s)<br\s*/?>', ' / ', x)
    x = re.sub(r'(?s)<[^>]+>', '', x)
    x = x.replace('&amp;', '&').replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    return re.sub(r'\s+', ' ', x).strip()


for i in ids:
    p = os.path.join(CACHE, i + '.html')
    s = open(p, 'rb').read().decode('utf-8', 'replace')
    out.write('===== %s =====\n' % i)
    # the free-text description block
    for m in re.finditer(r'class="(ticket-detail__content|block-ticket__lead|section__lead|ticket-info[^"]*|ticket-item__[^"]*)"[^>]*>(.*?)</div>', s, re.S):
        t = strip(m.group(2))
        if t and len(t) > 5:
            out.write('[%s] %s\n' % (m.group(1), t[:800]))
    out.write('\n')
out.close()
print('ok')
