# -*- coding: utf-8 -*-
# 「神保町マンゲキお笑いライブ」62件の公演日・受付（先行の締切／一般の締切）・発売日のまとまりを見る → mangeki_detail.txt
import io, json, re, collections
root = 'C:/Users/user/oshinavi/'
s = io.open(root + 'index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', s)
E, _ = json.JSONDecoder().raw_decode(s, m.start(1))
hit = sorted([e for e in E if e.get('name') == '神保町マンゲキお笑いライブ'], key=lambda e: (e['date'], e['dateLabel']))
out = io.open(root + 'tmp/x1001/mangeki_detail.txt', 'w', encoding='utf-8')
grp = collections.Counter()
for e in hit:
    pre = sorted({t.get('date') for t in e['tickets'] if '先行' in (t.get('type') or '')})
    gen = [t for t in e['tickets'] if t.get('type', '').startswith('一般')]
    gsd = sorted({t.get('startDate') or '-' for t in gen})
    grp[(e['date'][:7], tuple(pre), tuple(gsd))] += 1
    out.write(f"{e['id']} [{e.get('genre')}] {e.get('dateLabel')} | {e.get('artist')[:40]} | 先行締切{pre} 一般発売{gsd} 枠{len(e['tickets'])}\n")
out.write('\nまとまり（公演月・先行の締切・一般の発売日）\n')
for k, v in sorted(grp.items()):
    out.write(f'  {k} {v}件\n')
