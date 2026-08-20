"""EXILE型（キーワード部分一致で別グループを取り込む）の検出
監査レポートの「本命」ヒットのうち、公演名がアーティスト名と完全一致でないものを洗い出す。
（BALLISTIK BOYZ from EXILE TRIBE は "EXILE" を含むので本命に入ってしまう）
"""
import re, unicodedata

AUD = r'C:\Users\user\oshinavi\tmp\pia_missing_jpop_0802.txt'
OUT = r'C:\Users\user\oshinavi\tmp\grow_risk_0802.txt'


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・･,，.。!！?？\-‐―ー~〜/／「」『』()（）\[\]【】"\'’]+', '', s).lower()


txt = open(AUD, encoding='utf-8').read()
# 本命セクションだけ
head = txt.split('■ 別名義・フェス出演の候補')[0]

risky = []
cur_artist = None
for line in head.splitlines():
    m = re.match(r'● (.+?)\s+（ぴあのヒット', line)
    if m:
        cur_artist = m.group(1).strip()
        continue
    m2 = re.match(r'\s+\[(.+?)\] (.+)$', line)
    if m2 and cur_artist:
        perf = m2.group(2).strip()
        if norm(perf) != norm(cur_artist):
            risky.append((cur_artist, m2.group(1), perf))

L = ['=== EXILE型リスク＝公演名がアーティスト名と完全一致でない本命ヒット %d件 ===' % len(risky)]
L.append('（アーティスト名 | 券種 | ぴあ公演名）')
byart = {}
for a, k, p in risky:
    byart.setdefault(a, set()).add(p)
for a in sorted(byart, key=lambda x: -len(byart[x])):
    L.append('')
    L.append('● %s  … 別名の公演 %d種' % (a, len(byart[a])))
    for p in sorted(byart[a]):
        L.append('     %s' % p)

open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
print('risky-hits=%d artists=%d' % (len(risky), len(byart)))
