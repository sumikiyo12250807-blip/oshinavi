# -*- coding: utf-8 -*-
# 26629・26633 寺尾聰 Cover Live 1st/2nd を新着から外す＝ユーザー「チケット買えない　チケット情報のところ押せない　載せなくていい　直ったら拾ってきて」
#   → tools/tiget_watch.json に入れて毎朝の収集で個別ページを引く
import io, json, re
root = 'C:/Users/user/oshinavi/'
IDS = {26629, 26633}
text = io.open(root + 'index.html', encoding='utf-8', newline='').read()
io.open(root + 'index.html.bak_1001_del_terao', 'w', encoding='utf-8', newline='').write(text)
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
st = m.start(1)
E, end = json.JSONDecoder().raw_decode(text, st)
gone = [x for x in E if x['id'] in IDS]
E = [x for x in E if x['id'] not in IDS]
body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E) + '\n]'
text = text[:st] + body.replace('\n', '\r\n') + text[end:]
mo = re.search(r'NEW_ORDER\s*=\s*\[([^\]]*)\]', text)
ids = [x.strip() for x in mo.group(1).split(',') if x.strip() and int(x.strip()) not in IDS]
text = text[:mo.start(1)] + ','.join(ids) + text[mo.end(1):]
io.open(root + 'index.html', 'wb').write(text.encode('utf-8'))
L = ['', '## 昼：ユーザー「チケット情報のところ押せない　載せなくていい　直ったら拾ってきて」%d件（見張りリスト tools/tiget_watch.json へ）' % len(gone)]
for e in gone:
    u = next((t.get('url') for t in e['tickets'] if t.get('url')), '')
    L.append('- id=%d %s（%s）／ %s' % (e['id'], e.get('name'), e.get('dateLabel'), u))
io.open(root + 'logs/removed_2026-10-01.md', 'a', encoding='utf-8').write('\n'.join(L) + '\n')
print('外した', [e['id'] for e in gone])
