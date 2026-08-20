# -*- coding: utf-8 -*-
"""新着87件の総点検用ダンプ。ジャンル下書き(_genre)・ぴあ元カテゴリ(_piaSub)・会場・公演日・枠を並べる。
昨日(7/12)は _piaSub 空 → engeki 誤フォールバックが3件あった。そこを人が見る。"""
import re, json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))
NEW = [e for e in E if e.get('genre') == 'new']

cnt = collections.Counter(e.get('_genre') or '(空)' for e in NEW)
print(f'=== 新着 {len(NEW)}件 / ジャンル下書き内訳 ===')
for g, n in cnt.most_common():
    print(f'   {g}: {n}')

print('\n=== 全件（下書き / _piaSub / 公演名 / 会場 / 公演日 / 枠数）===')
for e in sorted(NEW, key=lambda x: (x.get('_genre') or '', x['id'])):
    sub = e.get('_piaSub')
    sub = sub if sub else '⚠️空'
    print(f"[{e.get('_genre') or '(空)':<8}] {sub:<12} id{e['id']} | {e.get('artist','')[:44]} | {e.get('venue','')[:30]} | {e.get('date','')} | {len(e.get('tickets',[]))}枠")
