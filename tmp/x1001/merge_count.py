# -*- coding: utf-8 -*-
# 画面でまとめる対象（index.html の _mKey と同じ考え方）が何枚のカード・何枚のバッジになるか数える → tmp/x1001/merge_count.txt
import io, json, re, collections, datetime
root = 'C:/Users/user/oshinavi/'
TODAY = datetime.date.today().isoformat()
text = io.open(root + 'index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
E, _ = json.JSONDecoder().raw_decode(text, m.start(1))
head = lambda tp: re.sub(r'[）)][^（）()]*$', '）', tp or '')
cards, before, after, ex = 0, 0, 0, []
for e in E:
    g = collections.defaultdict(list)
    for t in e.get('tickets') or []:
        if t.get('url') and not t.get('soldout') and not t.get('saleUntilSoldOut') and not t.get('saleEndUnknown') and (t.get('date') or '') >= TODAY:
            k = (t['url'], t.get('startDate') or '', re.sub(r'(?:R\d+年\s*)?\d{1,2}/\d{1,2}', 'D', head(t['type'])))
            g[k].append(t)
    gs = [v for v in g.values() if len(v) >= 2]
    if gs:
        cards += 1
        before += sum(len(v) for v in gs)
        after += len(gs)
        ex.append((sum(len(v) for v in gs) - len(gs), e['id'], e.get('name', '')[:36]))
ex.sort(reverse=True)
out = io.open(root + 'tmp/x1001/merge_count.txt', 'w', encoding='utf-8')
out.write(f'まとまるカード {cards}枚 / バッジ {before}枚 → {after}枚\n')
for n, i, nm in ex[:40]:
    out.write(f'  -{n} id{i} {nm}\n')
