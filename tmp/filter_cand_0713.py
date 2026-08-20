# -*- coding: utf-8 -*-
"""候補からNPBレギュラー戦を除外し、Jリーグ戦は保留に退避する。
NPB＝載せない方針（memory: feedback_baseball_scope・特設のみ可）。
Jリーグ＝方針未確定なのでユーザー回答待ちで別ファイルへ。"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

C = json.load(open('tmp/cand_0713.json', encoding='utf-8'))

NPB = re.compile(r'(スワローズ|ドラゴンズ|タイガース|カープ|ジャイアンツ|ベイスターズ|'
                 r'ホークス|ファイターズ|マリーンズ|バファローズ|ライオンズ|イーグルス).*対|'
                 r'対\s*(スワローズ|ドラゴンズ|タイガース|カープ|ジャイアンツ|ベイスターズ|'
                 r'ホークス|ファイターズ|マリーンズ|バファローズ|ライオンズ|イーグルス)')
JLEAGUE = re.compile(r'明治安田[ＪJ][１２３123]リーグ')

keep, npb, jl = [], [], []
for c in C:
    a = c.get('artist', '')
    if JLEAGUE.search(a):
        jl.append(c)
    elif NPB.search(a):
        npb.append(c)
    else:
        keep.append(c)

print(f'=== 除外 NPBレギュラー戦 {len(npb)}件 ===')
for c in npb:
    print(f"  {c.get('artist','')}")
print(f'\n=== 保留 Jリーグ戦 {len(jl)}件（ユーザー回答待ち）===')
for c in jl:
    print(f"  {c.get('artist','')}")
print(f'\n=== build対象 {len(keep)}件 → tmp/cand_0713_keep.json ===')

json.dump(keep, open('tmp/cand_0713_keep.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(jl, open('tmp/cand_0713_jleague.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
