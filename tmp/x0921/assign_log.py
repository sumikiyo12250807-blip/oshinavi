# -*- coding: utf-8 -*-
"""9/21夜の振り分け3,341件を、公演名・ジャンル・URLで logs/ に残す（ゲートC＝後から見られるリンク）。
対象＝振り分け前の控え（dry-runの出力）に出た id。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ids = [int(x) for x in io.open('tmp/x0921/assigned_ids.txt').read().split()]
h = io.open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))}
with io.open('logs/assign_0921_night.txt', 'w', encoding='utf-8') as f:
    f.write('# 2026-09-21夜 新着の振り分け（ユーザー「１」＝FANY・ZAIKO・ぴあ全部。駐車券 id17332・17333 は保留）\n')
    n = 0
    for i in ids:
        e = ev.get(i)
        if not e:
            continue
        L = e.get('links') or {}
        url = next((L[k] for k in ('fany', 'zaiko', 'pia', 'tiget', 'rakuten', 'eplus', 'lawson') if L.get(k)), '')
        f.write('id%s\t%s%s\t%s\t%s\n' % (i, e.get('genre'), ('+' + '+'.join(e['extraGenres'])) if e.get('extraGenres') else '',
                                        e.get('name'), url))
        n += 1
print('logs/assign_0921_night.txt に %d件' % n)
