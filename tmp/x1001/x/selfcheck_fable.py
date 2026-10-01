import re, io, glob, os
d = r'C:/Users/user/oshinavi/tmp/x1001/x'
ban = r"動く|動き|続く|続け|ひと押し|一押し|入れておく|取りにいって|あんた|生で浴び|押さえ|おさえ|両方|訪れ|やって来|ジャンル|のぶん|公演分|https://|手帳|メモして|カレンダー"
mat = io.open(os.path.join(d, 'material_posts.md'), encoding='utf-8').read().splitlines()
matlines = set(l.strip() for l in mat if re.match(r'^\d\d:\d\d ', l) or l.startswith('他にも'))
for n in range(4, 11):
    path = os.path.join(d, f'post{n:02d}.txt')
    p = io.open(path, encoding='utf-8').read().splitlines()
    print(f'--- post{n:02d} ({sum(len(l) for l in p)}字)')
    for i, l in enumerate(p, 1):
        for m in re.finditer(ban, l):
            print(f'  封印 L{i}: {m.group(0)} | {l}')
        if re.search(r'。(?!$)', l) and not re.match(r'^\d\d:\d\d ', l):
            print(f'  句点後に文字 L{i}: {l}')
    bad = [l for l in p if (re.match(r'^\d\d:\d\d ', l) or l.startswith('他にも')) and l.strip() not in matlines]
    cnt = sum(1 for l in p if re.match(r'^\d\d:\d\d ', l))
    print(f'  list lines={cnt} mismatched={bad}')
    times = sorted(set(re.match(r'^(\d\d:\d\d)', l).group(1) for l in p if re.match(r'^\d\d:\d\d ', l)))
    print(f'  times={times}')
