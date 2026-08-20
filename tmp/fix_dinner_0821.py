# -*- coding: utf-8 -*-
"""ディナーショーは「食事つきショー」と「アーティストのジャンル」の両方を持たせる
（ユーザー指示 2026-08-21「演歌とディナーショー2つに振り分ければいい」）。

既存データは片方しか付いていないものが混ざっていたので揃える。
もう片方が自明でない3件（179 ナジャ・グランディーバ／3231 YOSHIKI／4222 パク・ジュニョン）は
推測になるので**触らずユーザーに報告**する（[[feedback_no_speculation]]）。
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

# id: 足すジャンル（根拠は同じアーティストの既存エントリ）
ADD = {
    177:  'enka',        # 山内惠介＝演歌歌手
    726:  'dinnershow',  # 新浜レオン プレミアム・ディナーショー（同アーティストの3643が dinnershow+enka）
    2501: 'dinnershow',  # サラ・オレイン Dinner Live
    3167: 'dinnershow',  # 真田ナオキ ランチ&ディナーショー（775/3166 が enka）
    3929: 'classic',     # 千住真理子（3504/3717 が classic）
    3976: 'dinnershow',  # 純烈 Christmas Dinner Show（2405 が jpop）
    4119: 'dinnershow',  # 稲垣潤一 Christmas Dinner Show（615 が jpop）
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
n = 0
for e in EVENTS:
    g = ADD.get(e['id'])
    if not g:
        continue
    ex = list(e.get('extraGenres') or [])
    if g not in ex and g != e.get('genre'):
        ex.append(g)
        e['extraGenres'] = ex
    print('id=%-5d 主=%-11s サブ=%-16s %s' % (e['id'], e.get('genre'), str(ex), e.get('name')))
    n += 1
assert n == len(ADD), n
shutil.copyfile('index.html', 'index.html.bak_0821_dinner2')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('=== %d件 更新 ===' % n)
