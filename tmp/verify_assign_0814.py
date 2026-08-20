# -*- coding: utf-8 -*-
"""振り分け後の確認：45件に下書きが残っていないか／使ったジャンルがGENRE_LABELとフィルタに在るか。"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
h = open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
IDS = set(range(4176, 4226))
tgt = [e for e in EV if e['id'] in IDS]
print('対象 %d件' % len(tgt))
bad = [e['id'] for e in tgt if any(k in e for k in ('_genre', '_extraGenres', '_piaSub'))]
print('下書きキーが残っている:', bad or 'なし')
print('genre=new が残っている:', [e['id'] for e in tgt if e.get('genre') == 'new'] or 'なし')

used = sorted({e.get('genre') for e in tgt} | {g for e in tgt for g in (e.get('extraGenres') or [])})
labels = re.search(r'GENRE_LABEL\s*=\s*(\{.*?\})', h, re.S)
lab = labels.group(1) if labels else ''
btn = set(re.findall(r'data-genre="([a-z0-9.]+)"', h))
for g in used:
    print('  %-11s GENRE_LABEL:%s  フィルタボタン:%s' % (
        g, 'あり' if ('"%s"' % g) in lab or ("%s:" % g) in lab else '🚨無い',
        'あり' if g in btn else '🚨無い'))
