# -*- coding: utf-8 -*-
import json, io, re
hh = io.open('index.html', encoding='utf-8').read()
db = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', hh, re.S).group(1))
new = [e for e in db if e.get('genre') == 'new']
with io.open('tmp/newpool_peek_0905.txt','w',encoding='utf-8') as f:
    f.write('NEWPOOL=%d\n' % len(new))
    f.write('keys_union=%s\n\n' % ', '.join(sorted({k for e in new for k in e})))
    for e in new[-3:]:
        f.write(json.dumps(e, ensure_ascii=False, indent=1) + '\n\n')
    f.write('_genre有り=%d / 無し=%d\n' % (sum(1 for e in new if '_genre' in e), sum(1 for e in new if '_genre' not in e)))
print('OK')
