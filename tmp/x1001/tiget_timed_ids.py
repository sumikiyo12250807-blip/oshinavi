# -*- coding: utf-8 -*-
# TIGET の枠で「（… M/D HH:MM公演）」＝開場の時刻を公演と書いている枠を持つエントリを数える → tmp/x1001/tiget_timed_ids.json
import io, json, re
root = 'C:/Users/user/oshinavi/'
text = io.open(root + 'index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
E, _ = json.JSONDecoder().raw_decode(text, m.start(1))
ids, n = [], 0
for e in E:
    k = [t for t in e.get('tickets') or [] if 'tiget.net' in (t.get('url') or '')
         and re.search(r'\d{1,2}/\d{1,2} \d{1,2}:\d{2}公演）', t.get('type') or '')]
    if k:
        ids.append(e['id'])
        n += len(k)
json.dump(ids, io.open(root + 'tmp/x1001/tiget_timed_ids.json', 'w'))
io.open(root + 'tmp/x1001/tiget_timed_ids.txt', 'w', encoding='utf-8').write(f'{len(ids)}件 {n}枠\n')
