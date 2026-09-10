# -*- coding: utf-8 -*-
"""X投稿から主役枠の②野村萬斎と③春風亭昇太を外して5本にする。

ユーザー（2026-09-10）＝「２と３はいらない」
きっかけ＝「野村萬斎はXフォロワーがおおいの？」「春風亭昇太はフォロワーがおおいの？」
  野村萬斎 @mansai_gozaru … **19.3K**（2026-09-10 実測）＝主役に張るには少ない
  春風亭昇太 … **公式アカウントすら特定できず**

🚨あたしの落ち度＝台本は「翌日発売のうちXのフォロワーが多い上位3組」なのに、
  1回検索して出なかっただけで**知名度で決めていた**。数字で決めていなかった。

■ やること
  02（野村萬斎）と03（春風亭昇太）を外し、番号を詰める
  01（なとり）の予告を「狂言など伝統芸能」→「クラシックとジャズ」に直す
    ＝2本目が消えるので、予告の行き先が変わる
"""
import io
import os

D = 'tmp/xp0911'
KEEP = [1, 4, 5, 6, 7]          # なとり／クラシック／落語／音楽／舞台

texts = []
for n in KEEP:
    texts.append(io.open('%s/%02d.txt' % (D, n), encoding='utf-8').read().rstrip('\n'))

# 1本目の予告を直す（次はクラシックとジャズになる）
old = 'このあとの投稿では、狂言など伝統芸能の発売を並べるから、あたしのXをフォローして待っていて。'
new = 'このあとの投稿では、クラシックとジャズの発売を並べるから、あたしのXをフォローして待っていて。'
if old in texts[0]:
    texts[0] = texts[0].replace(old, new)
    print('① 1本目の予告を「クラシックとジャズ」に直した')
else:
    print('!! 1本目の予告が見つからない')

# 外した2本を退避（消さない）
os.makedirs(D + '/dropped', exist_ok=True)
for n in (2, 3):
    src = '%s/%02d.txt' % (D, n)
    if os.path.exists(src):
        io.open('%s/dropped/%02d.txt' % (D, n), 'w', encoding='utf-8', newline='\n').write(
            io.open(src, encoding='utf-8').read())
        os.remove(src)
        print('  %02d.txt を dropped/ へ退避した' % n)

# 番号を詰めて書き直す
for n in (4, 5, 6, 7):
    p = '%s/%02d.txt' % (D, n)
    if os.path.exists(p):
        os.remove(p)
for i, t in enumerate(texts, 1):
    p = '%s/%02d.txt' % (D, i)
    io.open(p, 'w', encoding='utf-8', newline='\n').write(t + '\n')
    print('  %s  %d字' % (p, len(t.replace('\n', ''))))

print('')
print('=== 5本になった ===')
