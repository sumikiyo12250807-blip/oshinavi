# -*- coding: utf-8 -*-
"""refresh_deadlines が「追加」する枠が、表記ゆれで既存とかぶっていないか調べる。
   ／ と / 、全角空白、【】〔〕 の違いだけで別枠に見えるのを拾う。"""
import io, json, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

built = {b['id']: b for b in json.load(io.open('tmp/blocked_built_0909.json', encoding='utf-8'))}
h = io.open('index.html', encoding='utf-8', newline='').read()
by = {e['id']: e for e in json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))}


def head(ty):
    m = re.match(r'^(.*?（[^（）]*公演）)', ty or '')
    return m.group(1) if m else (ty or '')


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・/／\-–—]', '', s)


sus = []
for i, b in built.items():
    e = by.get(i)
    if not e:
        continue
    cur_raw = {head(t.get('type')) for t in e.get('tickets') or []}
    cur_norm = {norm(k): k for k in cur_raw}
    for bt in b.get('tickets') or []:
        k = head(bt.get('type'))
        if k in cur_raw:
            continue          # そのまま一致＝更新側なので対象外
        if norm(k) in cur_norm:
            sus.append((i, e.get('name', '')[:26], k, cur_norm[norm(k)]))

print('表記ゆれで二重になりそうな追加 %d枠' % len(sus))
for i, name, newk, oldk in sus:
    print('  id%-6d %s\n      追加しようとしている: %s\n      既存にある枠        : %s' % (i, name, newk, oldk))
