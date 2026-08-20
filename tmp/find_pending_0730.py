# -*- coding: utf-8 -*-
"""index.html のJSONエントリから、前日持ち越しの削除候補(e+系)を機械抽出"""
import io, json, re

raw = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+(?:EVENTS|events)\s*=\s*\[', raw)
print('EVENTS宣言:', bool(m), m.group(0) if m else '')

# JSON配列の抽出（宣言位置から括弧の対応で切る）
if m:
    s = raw.index('[', m.start())
    depth = 0
    for i in range(s, len(raw)):
        c = raw[i]
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                e = i + 1
                break
    arr = json.loads(raw[s:e])
    print('エントリ総数: %d' % len(arr))
    keys = ['米倉', 'ハルナ', '遠藤響子', 'REBECCA', '玉置']
    hits = []
    for ev in arr:
        blob = (ev.get('artist') or '') + ' ' + (ev.get('name') or '')
        for k in keys:
            if k in blob:
                hits.append((ev['id'], ev.get('artist'), ev.get('date'),
                             [(t.get('type'), t.get('date')) for t in ev.get('tickets', [])],
                             ev.get('links', {})))
    out = []
    for h in hits:
        out.append(json.dumps(h, ensure_ascii=False, indent=1))
    io.open('tmp/out_pending_0730.txt', 'w', encoding='utf-8').write('\n'.join(out) or '(該当なし)')
    print('該当 %d 件 → tmp/out_pending_0730.txt' % len(hits))
