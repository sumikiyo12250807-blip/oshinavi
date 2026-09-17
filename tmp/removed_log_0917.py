import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
html = open('index.html.bak_0917_del_ended', encoding='utf-8').read()
EV = {e['id']: e for e in json.loads(re.search(r'const EVENTS\s*=\s*(\[[\s\S]*?\]);', html).group(1))}
ids = [1027, 2326, 2997, 6244, 6328, 6416, 7469, 7967, 8054, 8658, 8666, 8828, 9621, 9704, 9805, 9885, 10397]
out = ['# 削除 2026-09-17（朝のルーチン・公演終了）', '',
       '判定＝check_expired の「公演終了」18件 → 別エージェントが「削除は誤り」の前提で index.html から独立に読み直し → 17件とも公演日・締切がすべて 9/16 以前。',
       '残した＝1904 劇団かもめんたる（e+ 配信の視聴券が 10/4 21:00 まで買える）。予備 index.html.bak_0917_del_ended', '']
for i in ids:
    e = EV[i]
    links = e.get('links') or {}
    url = links.get('pia') or links.get('eplus') or links.get('rakuten') or next((t.get('url') for t in e.get('tickets', []) if t.get('url')), '') or '(URLなし)'
    out.append(f"- id{i} {e.get('artist','')}｜{e.get('venue','')}｜公演 {e.get('date','')}｜{url}")
open('logs/removed_2026-09-17.md', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out[5:]))
