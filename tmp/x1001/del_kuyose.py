# -*- coding: utf-8 -*-
# 26765 区寄席（TIGET 526238）を新着から消す＝ユーザー「これは消されてた」（売り場のページが消えている・403）
import io, json, re
root = 'C:/Users/user/oshinavi/'
ID = 26765
text = io.open(root + 'index.html', encoding='utf-8', newline='').read()
io.open(root + 'index.html.bak_1001_del%d' % ID, 'w', encoding='utf-8', newline='').write(text)
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
st = m.start(1)
E, end = json.JSONDecoder().raw_decode(text, st)
e = next(x for x in E if x['id'] == ID)
url = next((t.get('url') for t in e['tickets'] if t.get('url')), '')
E = [x for x in E if x['id'] != ID]
body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E) + '\n]'
text = text[:st] + body.replace('\n', '\r\n') + text[end:]
mo = re.search(r'NEW_ORDER\s*=\s*\[([^\]]*)\]', text)
ids = [x.strip() for x in mo.group(1).split(',') if x.strip() and int(x.strip()) != ID]
text = text[:mo.start(1)] + ','.join(ids) + text[mo.end(1):]
io.open(root + 'index.html', 'wb').write(text.encode('utf-8'))
io.open(root + 'logs/removed_2026-10-01.md', 'a', encoding='utf-8').write(
    '\n## 昼：ユーザー「これは消されてた」1件\n- id=%d %s（%s）／ %s\n' % (ID, e.get('name'), e.get('dateLabel'), url))
print('消した', ID, e.get('name'), url)
