# -*- coding: utf-8 -*-
"""「このアーティストの他の公演」導線が何件作れるかの実測。
外部に飛ばさずサイト内で回遊させる素材がDBにどれだけあるかを数える。"""
import re, json, sys, unicodedata, collections
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S).group(1))

def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—]', '', s).lower()

by_artist = collections.defaultdict(list)
for e in EVENTS:
    a = norm(e.get('artist'))
    if a:
        by_artist[a].append(e)

multi = {k: v for k, v in by_artist.items() if len(v) >= 2}
n_ev_in_multi = sum(len(v) for v in multi.values())

print(f'総エントリ {len(EVENTS)}件 / ユニークartist {len(by_artist)}組')
print(f'同じアーティストで2件以上ある: {len(multi)}組 = {n_ev_in_multi}件'
      f'（全体の{n_ev_in_multi*100//len(EVENTS)}%）')
print()
print('■ 公演数が多い順（内部回遊のネタが濃い子）')
for k, v in sorted(multi.items(), key=lambda x: -len(x[1]))[:15]:
    print(f'  {len(v):3d}件  {v[0].get("artist")[:34]}')

# 同じ県で近い時期の公演＝「近くのイベント」導線の厚み
by_pref = collections.defaultdict(int)
for e in EVENTS:
    for p in re.split(r'[・/／]', e.get('prefecture') or ''):
        if p:
            by_pref[p] += 1
print()
print('■ 県別エントリ数（上位10・「あなたの県の近い公演」導線の厚み）')
for p, n in sorted(by_pref.items(), key=lambda x: -x[1])[:10]:
    print(f'  {n:4d}件  {p}')
print(f'  …計{len(by_pref)}県')

# ジャンル別
by_genre = collections.Counter(e.get('genre') for e in EVENTS)
print()
print('■ ジャンル別（上位10）')
for g, n in by_genre.most_common(10):
    print(f'  {n:4d}件  {g}')
