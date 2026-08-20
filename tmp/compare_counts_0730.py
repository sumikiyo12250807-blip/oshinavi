# -*- coding: utf-8 -*-
"""index.html と各バックアップ・git原本のエントリ数／該当アーティスト有無を比較"""
import io, json, re, subprocess, sys

KEYS = ['米倉', 'ハルナ', '遠藤響子', 'REBECCA', '玉置']

def parse(raw, label):
    m = re.search(r'const\s+EVENTS\s*=\s*\[', raw)
    if not m:
        return '%s: EVENTS宣言なし' % label
    s = raw.index('[', m.start())
    depth = 0
    for i in range(s, len(raw)):
        if raw[i] == '[':
            depth += 1
        elif raw[i] == ']':
            depth -= 1
            if depth == 0:
                e = i + 1
                break
    arr = json.loads(raw[s:e])
    hit = []
    for ev in arr:
        blob = (ev.get('artist') or '') + ' ' + (ev.get('name') or '')
        for k in KEYS:
            if k in blob:
                hit.append('%s(id%s)' % (k, ev['id']))
    return '%s: %d件  該当[%s]' % (label, len(arr), ','.join(hit) or 'なし')

lines = []
lines.append(parse(io.open('index.html', encoding='utf-8', newline='').read(), '現行 index.html'))
for bak in ('index.html.bak_0730_heal_stale', 'index.html.bak_0730_rescue'):
    try:
        lines.append(parse(io.open(bak, encoding='utf-8', newline='').read(), bak))
    except IOError:
        lines.append('%s: 無し' % bak)

git = subprocess.run(['git', 'show', 'HEAD:index.html'], capture_output=True)
lines.append(parse(git.stdout.decode('utf-8', 'replace'), 'git HEAD:index.html'))

io.open('tmp/out_counts_0730.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(l.encode('ascii', 'replace').decode('ascii') for l in lines))
