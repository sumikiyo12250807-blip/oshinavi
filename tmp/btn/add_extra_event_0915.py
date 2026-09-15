# -*- coding: utf-8 -*-
"""進撃の巨人（キッズ）に2つ目のジャンル「イベント」を足す（2026-09-15 夜）
ユーザー「進撃の巨人はキッズマークつけてもいいけど、大人も探せるようにしてね」→「イベントを足して」
・名前に「進撃の巨人」が入っていて genre が kids、まだ extraGenres が無いエントリだけ
・"genre": "kids", の次の行に extraGenres を3行で足す（ほかのエントリと同じ書き方）
・改行は CRLF のまま（newline='' で読み書き＝Pythonで書き戻すと LF になる罠を避ける）
・書いたあと EVENTS をパースして、足した件数・extraGenres の中身・全体の件数を数える
使い方: python add_extra_event_0915.py
"""
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'


def events(text):
    return json.loads(re.search(r'  const EVENTS = (\[.*?\]);', text, re.S).group(1))


with open(P, encoding='utf-8', newline='') as f:
    text = f.read()
before = events(text)
shutil.copyfile(P, 'index.html.bak_0915_shingeki_event')

lines = text.split('\r\n')
out, i, added = [], 0, []
cur = None
while i < len(lines):
    ln = lines[i]
    if ln == '  {':
        # エントリの終わりまでを見て、条件に合うか決める
        j = i
        while not lines[j].startswith('  }'):
            j += 1
        block = lines[i:j + 1]
        name = next((b for b in block if b.startswith('    "name": ')), '')
        is_target = ('進撃の巨人' in name and '    "genre": "kids",' in block
                     and not any(b.startswith('    "extraGenres"') for b in block))
        for b in block:
            out.append(b)
            if is_target and b == '    "genre": "kids",':
                out += ['    "extraGenres": [', '      "event"', '    ],']
        if is_target:
            idl = next((b for b in block if b.startswith('    "id": ')), '')
            added.append(idl.split(':')[1].strip().rstrip(','))
        i = j + 1
        continue
    out.append(ln)
    i += 1

new = '\r\n'.join(out)
after = events(new)
assert len(after) == len(before), '件数が変わった'
sg = [e for e in after if '進撃の巨人' in (e.get('name') or '')]
bad = [e['id'] for e in sg if e.get('genre') == 'kids' and e.get('extraGenres') != ['event']]
assert not bad, 'extraGenres が付いていない: %s' % bad
with open(P, 'w', encoding='utf-8', newline='') as f:
    f.write(new)
print('足した %d件: %s' % (len(added), ','.join(added)))
print('進撃の巨人の全エントリ %d件（キッズで extraGenres=["event"] でないもの 0件）／全体 %d件は変わらず' % (len(sg), len(after)))
print('予備: index.html.bak_0915_shingeki_event')
