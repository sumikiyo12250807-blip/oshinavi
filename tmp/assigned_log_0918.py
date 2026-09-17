# -*- coding: utf-8 -*-
# 振り分けの記録＝公演名＋ジャンル＋確認用URL（URLはindex.htmlから機械抽出）
import re, json, io

bak = open('index.html.bak_0918_assign', encoding='utf-8', newline='').read()
cur = open('index.html', encoding='utf-8', newline='').read()
before = json.loads(re.search(r'const EVENTS = (\[.*?\]);', bak, re.S).group(1))
after = json.loads(re.search(r'const EVENTS = (\[.*?\]);', cur, re.S).group(1))
was_new = {e['id'] for e in before if e.get('genre') == 'new'}
now = {e['id']: e for e in after}

rows = []
for i in sorted(was_new):
    e = now.get(i)
    if not e or e.get('genre') == 'new':
        continue
    L = e.get('links') or {}
    url = next((L[k] for k in ('pia', 'rakuten', 'lawson', 'eplus') if L.get(k)), '')
    g = e.get('genre')
    extra = e.get('extraGenres') or []
    rows.append((i, g + ('+' + '+'.join(extra) if extra else ''), e.get('artist', ''),
                 e.get('venue', ''), e.get('date', ''), url))

o = io.open('logs/assigned_2026-09-18.md', 'w', encoding='utf-8')
o.write('# 2026-09-18 朝 振り分け（ぴあ由来 %d件）\n\n' % len(rows))
o.write('ジャンルは `tools/build_pia_entries.py` の `PIA_GENRE_MAP`／`PIA_CAT_FALLBACK`／`genre_from_subcat()` で\n')
o.write('ぴあのカテゴリをそのまま機械で写したもの。別エージェントに判定案を伏せてゼロから導かせ、95件とも一致（割れ0件）。\n\n')
by_g = {}
for r in rows:
    by_g.setdefault(r[1], []).append(r)
for g in sorted(by_g, key=lambda x: (-len(by_g[x]), x)):
    o.write(f"\n## {g}（{len(by_g[g])}件）\n")
    for r in by_g[g]:
        o.write(f"- id{r[0]} {r[2]} @ {r[3]}（公演 {r[4]}）\n")
        o.write(f"  - {r[5] or '（URLなし）'}\n")
o.close()
print('ok', len(rows))
