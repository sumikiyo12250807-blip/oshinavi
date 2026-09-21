# -*- coding: utf-8 -*-
"""締切側に「R9年」を付けてしまっている枠を数える（売り場別）。
既存の流儀＝**公演日（カッコの中）にはR9年を付ける／締切（カッコの後の〜）には年を付けない**。
🚨判定は「）〜」で切る＝カッコ閉じの後ろが締切。公演日の範囲の「〜」で切ると誤判定する。
"""
import collections, io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
h = io.open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))


def vendor(t, e):
    u = (t.get('url') or '') + json.dumps(e.get('links') or {}, ensure_ascii=False)
    for k, pat in (('fany', 'fany.lol'), ('tiget', 'tiget.net'), ('zaiko', 'zaiko.io'),
                   ('pia', 'pia.jp'), ('eplus', 'eplus.jp'), ('rakuten', 'rakuten')):
        if pat in u:
            return k
    return 'その他'


bad = collections.Counter()
tot = collections.Counter()
examples = collections.defaultdict(list)
for e in ev:
    for t in e.get('tickets') or []:
        ty = t.get('type') or ''
        if '）〜' not in ty:
            continue
        v = vendor(t, e)
        tot[v] += 1
        tail = ty.split('）〜', 1)[1]
        if re.search(r'R\d+年', tail):
            bad[v] += 1
            if len(examples[v]) < 4:
                examples[v].append((e['id'], ty))

out = io.open('tmp/x0921/r9_on_deadline.txt', 'w', encoding='utf-8')
out.write('=== 締切側に「R9年」を付けている枠（売り場別）===\n')
out.write('%-10s %8s / %8s\n' % ('売り場', '付いてる', '締切つき全体'))
for v in sorted(tot, key=lambda x: -bad[x]):
    out.write('%-10s %8d / %8d\n' % (v, bad[v], tot[v]))
out.write('\n合計 %d枠 / 締切つき %d枠\n' % (sum(bad.values()), sum(tot.values())))
for v, xs in examples.items():
    out.write('\n--- %s の例 ---\n' % v)
    for i, ty in xs:
        out.write('  id%-6s %s\n' % (i, ty[:88]))
out.close()
print('締切にR9年 %d枠 / 締切つき全体 %d枠 → tmp/x0921/r9_on_deadline.txt'
      % (sum(bad.values()), sum(tot.values())))
