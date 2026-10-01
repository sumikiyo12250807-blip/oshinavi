# -*- coding: utf-8 -*-
# 新着のうち番人＋独立チェックを通った分の id を書き出す（保留5件は残す）＋迷ったら両方の2件にジャンルを足す
import io, json, re
root = 'C:/Users/user/oshinavi/'
HOLD = {26594, 26562, 26629, 26633, 26765}
ADD = {26586: 'rock', 26792: 'jpop'}
text = io.open(root + 'index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
st = m.start(1)
E, end = json.JSONDecoder().raw_decode(text, st)
for e in E:
    if e['id'] in ADD and e.get('genre') == 'new':
        g = ADD[e['id']]
        if g != e.get('_genre') and g not in (e.get('_extraGenres') or []):
            e['_extraGenres'] = (e.get('_extraGenres') or []) + [g]
body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E) + '\n]'
io.open(root + 'index.html', 'wb').write((text[:st] + body.replace('\n', '\r\n') + text[end:]).encode('utf-8'))
ids = [e['id'] for e in E if e.get('genre') == 'new' and e['id'] not in HOLD]
json.dump(ids, io.open(root + 'tmp/x1001/pool_assign_ids.json', 'w'))
io.open(root + 'tmp/x1001/pool_assign_prep.txt', 'w', encoding='utf-8').write(f'振り分け {len(ids)}件 / 保留 {len(HOLD)}件\n')
