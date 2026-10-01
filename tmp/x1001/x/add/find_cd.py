# -*- coding: utf-8 -*-
import io, json, re, sys
root = 'C:/Users/user/oshinavi/'
s = io.open(root + 'index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', s)
E, _ = json.JSONDecoder().raw_decode(s, m.start(1))
out = io.open(root + 'tmp/x1001/x/add/find_cd.txt', 'w', encoding='utf-8')
for e in E:
    js = json.dumps(e, ensure_ascii=False)
    if sys.argv[1] in js:
        out.write(f"{e['id']} [{e.get('genre')}] {e.get('name')} | {e.get('dateLabel')}\n")
        for t in e['tickets']:
            if sys.argv[1] in (t.get('url') or '') or not t.get('url'):
                out.write(f"   {t.get('type')} | {t.get('startDate')}〜{t.get('date')} | {t.get('url')}\n")
