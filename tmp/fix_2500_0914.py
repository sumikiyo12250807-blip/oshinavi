# -*- coding: utf-8 -*-
"""id2500「ドラゴンクエスト」ウインドオーケストラコンサートに、未登録だった4次・5次プリセールを足す（2026-09-14 朝）。
ヒール本体の取り直し（tmp/heal_stale.json）は東京公演のページ（eventCd=2627834）だけから組まれていて、
栃木・千葉など他の会場の枠を持たない＝そのまま当てると他会場が消えるので安全弁が止めた。
→ 置き換えずに「いまの登録に無い券種名の枠」だけを足す（url は取り直しが持っている東京のページ）。

使い方: python tmp/fix_2500_0914.py [--apply]
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
ID = 2500
built = next(h for h in json.load(io.open('tmp/heal_stale.json', encoding='utf-8')) if h['id'] == ID)

src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == ID)
have = {t.get('type') for t in e.get('tickets') or []}
add = [t for t in built['tickets'] if t.get('type') not in have]
print('いま %d枠 / 足す %d枠' % (len(e.get('tickets') or []), len(add)))
for t in add:
    assert t.get('url'), 'url の無い枠は足さない'
    print('   + %s | date=%s | %s' % (t['type'], t.get('date'), t['url']))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
e['tickets'] = list(e.get('tickets') or []) + add
nl = '\r\n' if '\r\n' in src else '\n'
body = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
io.open('index.html', 'w', encoding='utf-8', newline='').write(src[:m.start()] + m.group(1) + body + m.group(3) + src[m.end():])
print('書き込み完了')
