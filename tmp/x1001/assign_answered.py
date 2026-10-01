# -*- coding: utf-8 -*-
"""10/1朝：9/30夜にユーザーが答えた件だけ振り分ける
 ⑩ 売り場の札を全部写す（TIGET 25163・25171・25175／ZAIKO Dance→dance 25144・25970）
 ⑯ 推し活に入れる＝載せる（25396 TRPG相談会・26229 ビザンBASECAMP）→ event
使い方: python tmp/x1001/assign_answered.py [--apply]
"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
IDS = {25163, 25171, 25175, 25144, 25970, 25396, 26229}
TITLE = '朝：9/30夜の答えどおり %d件（⑩売り場の札を全部写す／⑯載せる）'
if '--ids' in sys.argv:  # 使い方2: --ids 1,2 --title "見出し %d件"
    v = sys.argv[sys.argv.index('--ids') + 1]
    IDS = set(json.load(io.open(v))) if v.endswith('.json') else {int(x) for x in v.split(',')}
    TITLE = sys.argv[sys.argv.index('--title') + 1]
root = 'C:/Users/user/oshinavi/'
text = io.open(root + 'index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
st = m.start(1)
E, end = json.JSONDecoder().raw_decode(text, st)
go = [e for e in E if e['id'] in IDS and e.get('genre') == 'new' and e.get('_genre')]
for e in go:
    print(e['id'], e['_genre'], e.get('_extraGenres'), e.get('name', '')[:40])
if len(go) != len(IDS):
    print('!! 見つからない id', IDS - {e['id'] for e in go}); sys.exit(1)
if not APPLY:
    sys.exit(0)
for e in go:
    e['genre'] = e['_genre']
    if e.get('_extraGenres'):
        e['extraGenres'] = [g for g in dict.fromkeys(e['_extraGenres']) if g != e['genre']]
# 読んだ時の形（1件1行か indent=2 か）を保つ
compact = '\n{"id"' in text[st:st + 200].replace('\r\n', '\n') or text[st:st + 3].startswith('[\r\n{') or text[st:st + 3].startswith('[\n{')
if compact:
    body = '[\n' + ',\n'.join(json.dumps(e, ensure_ascii=False, separators=(',', ':')) for e in E) + '\n]'
else:
    body = json.dumps(E, ensure_ascii=False, indent=2)
if '\r\n' in text[st:st + 3000]:
    body = body.replace('\r\n', '\n').replace('\n', '\r\n')
text = text[:st] + body + text[end:]
mo = re.search(r'NEW_ORDER\s*=\s*\[([^\]]*)\]', text)
ids = [x.strip() for x in mo.group(1).split(',') if x.strip() and int(x.strip()) not in IDS]
text = text[:mo.start(1)] + ','.join(ids) + text[mo.end(1):]
io.open(root + 'index.html', 'wb').write(text.encode('utf-8'))


def url(e):
    return next((t.get('url') for t in e.get('tickets') or [] if t.get('url')), '')


L = ['', '## ' + TITLE % len(go)]
for e in sorted(go, key=lambda x: x['id']):
    L.append('- id=%s %s → %s%s ／ %s' % (e['id'], e.get('name', '')[:50], e['genre'],
             ('＋' + '・'.join(e['extraGenres'])) if e.get('extraGenres') else '', url(e)))
io.open(root + 'logs/assigned_2026-10-01.md', 'a', encoding='utf-8').write('\n'.join(L) + '\n')
print('書いた')
