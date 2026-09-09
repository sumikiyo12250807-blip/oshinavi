# -*- coding: utf-8 -*-
"""新着(genre=="new")のぴあ由来エントリについて、_piaSub と _genre が
PIA_GENRE_MAP（genre_from_subcat）どおりかを機械で突合する。読み取り専用。"""
import json, re, sys, io, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
import build_pia_entries as B
sys.stdout = io.TextIOWrapper(open(sys.__stdout__.fileno(), 'wb', closefd=False), encoding='utf-8')

IDX = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
src = open(IDX, encoding='utf-8').read()

i = src.index('const EVENTS = [')
start = src.index('[', i)
# 括弧の対応で終端を取る（文字列内の括弧は無視）
depth, j, instr, esc = 0, start, False, False
while j < len(src):
    c = src[j]
    if instr:
        if esc: esc = False
        elif c == '\\': esc = True
        elif c == '"': instr = False
    else:
        if c == '"': instr = True
        elif c == '[': depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                break
    j += 1
events = json.loads(src[start:j+1])
print('EVENTS 総数 =', len(events))

new = [e for e in events if e.get('genre') == 'new']
print('genre=="new" =', len(new))

pia = [e for e in new if (e.get('links') or {}).get('pia')]
nonpia = [e for e in new if not (e.get('links') or {}).get('pia')]
print('うち links.pia あり =', len(pia), ' / なし =', len(nonpia))

def split_sub(s):
    if not s:
        return (None, None)
    if '/' in s:
        a, b = s.split('/', 1)
        return (a, b)
    return (None, s)

ok, mismatch, nosub, noexp = [], [], [], []
for e in pia:
    raw = e.get('_piaSub') or ''
    cat, sub = split_sub(raw)
    name = e.get('artist') or e.get('name') or ''
    if not sub:
        nosub.append(e); continue
    exp = B.genre_from_subcat(cat, sub, name)
    if not exp:
        noexp.append((e, raw)); continue
    g = e.get('_genre')
    if g == exp[0]:
        ok.append(e)
    else:
        mismatch.append((e, raw, exp[0], g))

def line(e, raw, extra=''):
    u = (e.get('links') or {}).get('pia') or ''
    return 'id%s %s ｜_piaSub=%s ｜_genre=%s %s ｜%s' % (
        e.get('id'), e.get('artist') or e.get('name'), raw, e.get('_genre'), extra, u)

print('\n=== 対応表どおり %d件 / ズレ %d件 ===' % (len(ok), len(mismatch)))
for e, raw, exp, g in mismatch:
    print(line(e, raw, '→期待=%s' % exp))

print('\n=== _piaSub が空(ぴあ由来だが区分不明) %d件 ===' % len(nosub))
for e in nosub:
    print(line(e, '(空)'))

print('\n=== 対応表で行き先が決まらない(genre_from_subcat=None) %d件 ===' % len(noexp))
for e, raw in noexp:
    print(line(e, raw))

# 個別の洗い出し
print('\n=== 海外ROCK・POPS なのに yougaku/kpop でない ===')
n = 0
for e in new:
    raw = e.get('_piaSub') or ''
    if '海外ROCK・POPS' in raw and e.get('_genre') not in ('yougaku', 'kpop'):
        print(line(e, raw)); n += 1
print('該当 %d件' % n)

print('\n=== 海外ROCK・POPS の全件（kpop/yougaku の振り分け確認用） ===')
n = 0
for e in new:
    raw = e.get('_piaSub') or ''
    if '海外ROCK・POPS' in raw:
        print(line(e, raw)); n += 1
print('該当 %d件' % n)

print('\n=== _piaSub に「伝統」を含む ===')
n = 0
for e in new:
    raw = e.get('_piaSub') or ''
    if '伝統' in raw:
        print(line(e, raw)); n += 1
print('該当 %d件' % n)

print('\n=== _genre が hougaku / dento のもの（振り分け妥当性の目視用） ===')
n = 0
for e in new:
    if e.get('_genre') in ('hougaku', 'dento'):
        print(line(e, e.get('_piaSub') or '(空)')); n += 1
print('該当 %d件' % n)

print('\n=== _genre が空/None ===')
n = 0
for e in new:
    if not e.get('_genre'):
        u = (e.get('links') or {}).get('pia') or (e.get('links') or {}).get('official') or ''
        print('id%s %s ｜_piaSub=%s ｜links=%s ｜%s' % (
            e.get('id'), e.get('artist') or e.get('name'),
            e.get('_piaSub') or '(空)', ','.join((e.get('links') or {}).keys()), u)); n += 1
print('該当 %d件' % n)

print('\n=== ぴあ以外の新着（参考・_genreの出所別） ===')
from collections import Counter
c = Counter()
for e in nonpia:
    c[','.join(sorted((e.get('links') or {}).keys()))] += 1
for k, v in c.most_common():
    print(k, v)

# 全新着の _genre 分布
print('\n=== 新着の _genre 分布 ===')
c2 = Counter(e.get('_genre') or '(空)' for e in new)
for k, v in c2.most_common():
    print(k, v)

# ぴあ由来の _piaSub 分布
print('\n=== ぴあ由来の _piaSub 分布 ===')
c3 = Counter((e.get('_piaSub') or '(空)') for e in pia)
for k, v in c3.most_common():
    print(k, v)
