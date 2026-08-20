# -*- coding: utf-8 -*-
"""正しい境界でエントリ削除。ブロック開始は '{ + idキー' の明示マッチ。"""
import json, io, sys, shutil, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def arrlen(txt):
    i = txt.index('const EVENTS = [') + len('const EVENTS = ')
    return len(json.JSONDecoder().raw_decode(txt, i)[0])

def delete_ids(path, ids, brace, idind, bak):
    txt = open(path, encoding='utf-8').read()
    before = arrlen(txt)
    new = txt
    for eid in ids:
        marker = f'{brace}{{\n{idind}"id": {eid},\n'
        start = new.find(marker)
        if start < 0:
            print(f"  !! id{eid} not found"); continue
        m = re.search('\\n' + re.escape(brace) + '\\},\\n', new[start:])
        end = start + m.end()
        # consume trailing blank/whitespace-only line(s)
        m2 = re.match(r'(?:[ \t]*\n)+', new[end:])
        if m2:
            end += m2.end()
        new = new[:start] + new[end:]
    after = arrlen(new)
    shutil.copy(path, bak)
    open(path, 'w', encoding='utf-8').write(new)
    print(f"{path}: {before} -> {after} (削除{before-after}件)")

delete_ids('index.html', [416,441,515,542,547,679,691,816,899,951,968,974,228,258,393],
           '  ', '    ', 'index.html.bak_0621_morning_delete')
delete_ids('events.html', [85,143,279,456,745],
           '      ', '            ', 'events.html.bak_0621_morning_delete')
