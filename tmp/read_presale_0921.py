# -*- coding: utf-8 -*-
"""ぴあ発売前ハーベストの結果（tmp/x0921/presale_*.json）の数字をまとめて読む。"""
import glob, io, json, os, sys

out = io.open('tmp/x0921/presale_summary.txt', 'w', encoding='utf-8')
tot_new = 0
for p in sorted(glob.glob('tmp/x0921/presale_*.json')):
    d = json.load(open(p, encoding='utf-8'))
    n = len(d.get('new') or [])
    tot_new += n
    out.write('%-34s lg=%-4s 総%-6s ページ%-4s 解析%-5s 未登録%-5s 既存名一致%s\n'
              % (os.path.basename(p), d.get('lg'), d.get('total'), d.get('pages'),
                 d.get('parsed'), n, d.get('new_name_in_db')))
out.write('\n未登録の合計 %d件\n' % tot_new)
out.close()
print(open('tmp/x0921/presale_summary.txt', encoding='utf-8').read())
