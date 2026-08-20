# -*- coding: utf-8 -*-
"""index.html から15件、events.html から5件を削除（span除去・クリーン差分）。"""
import json, io, sys, shutil, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def count(path):
    txt = open(path, encoding='utf-8').read()
    i = txt.index('const EVENTS = [') + len('const EVENTS = ')
    arr, _ = json.JSONDecoder().raw_decode(txt, i)
    return txt, arr

def delete_ids(path, ids, bak):
    txt, arr = count(path)
    before = len(arr)
    new = txt
    for eid in ids:
        idkey = f'\n    "id": {eid},\n'
        idpos = new.find(idkey)
        if idpos < 0:
            print(f"  !! id{eid} not found in {path}"); continue
        # entry start = the '  {' line before id
        start = new.rfind('\n  {\n', 0, idpos)
        # entry end = closing '\n  },' + newline + optional blank line
        m = re.search(r'\n  \},\n(\n)?', new[idpos:])
        end = idpos + m.end()
        new = new[:start+1] + new[end:]
    # recount
    i = new.index('const EVENTS = [') + len('const EVENTS = ')
    arr2, _ = json.JSONDecoder().raw_decode(new, i)
    after = len(arr2)
    shutil.copy(path, bak)
    open(path, 'w', encoding='utf-8').write(new)
    print(f"{path}: {before} -> {after} (削除{before-after}件) backup={bak}")

delete_ids('index.html', [416,441,515,542,547,679,691,816,899,951,968,974,228,258,393],
           'index.html.bak_0621_morning_delete')
delete_ids('events.html', [85,143,279,456,745],
           'events.html.bak_0621_morning_delete')
