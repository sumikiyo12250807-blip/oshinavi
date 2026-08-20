# -*- coding: utf-8 -*-
"""7/6 期限切れ削除56件（ユーザーOK「削除でOK」）。
A=公演終了3件(32/445/1398)＋B=抽選結果発表前/終了53件。id1582は7/7発表で保留=除外。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv

A = [32, 445, 1398]
lines = open('tmp/del_cand_0706.txt', encoding='utf-8').read().splitlines()
B = [int(l.split('\t')[0][2:]) for l in lines if l and not l.startswith('id1582')]
DEL = set(A) | set(B)

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
before = len(EVENTS)
removed = [e for e in EVENTS if e.get('id') in DEL]
kept = [e for e in EVENTS if e.get('id') not in DEL]
print(f"削除対象 {len(DEL)}件 / 実際に除去 {len(removed)}件")
missing = DEL - {e.get('id') for e in removed}
if missing:
    print(f"!! DB内に見つからないid: {sorted(missing)}")
print(f"=== {before} -> {len(kept)} ===")
if DRY:
    print("(DRY)")
else:
    new_arr = json.dumps(kept, ensure_ascii=False, indent=2)
    open('index.html.bak_0706_morning_delete', 'w', encoding='utf-8').write(h)
    open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print("written (backup: index.html.bak_0706_morning_delete)")
