import re

NEW_IDS = set(range(855, 937))  # 855..936
EXTRA_IDS = {899, 922, 903, 907}  # ones I added extraGenres to

lines = open('index.html', encoding='utf-8', newline='').read().split('\r\n')
out = []
cur_id = None
reverted = 0
extra_removed = 0
id_re = re.compile(r'^\s*"id":\s*(\d+),')
genre_re = re.compile(r'^(\s*)"genre":\s*"[^"]*"(,?)\s*$')
extra_re = re.compile(r'^\s*"extraGenres":\s*\[')
for ln in lines:
    m = id_re.match(ln)
    if m:
        cur_id = int(m.group(1))
    if cur_id in NEW_IDS:
        # drop extraGenres lines I added
        if extra_re.match(ln):
            extra_removed += 1
            continue
        gm = genre_re.match(ln)
        if gm:
            out.append(f'{gm.group(1)}"genre": "new"{gm.group(2)}')
            reverted += 1
            continue
    out.append(ln)

text = '\r\n'.join(out)

# restore NEW_ORDER: 3 consultation ids first, then rest ascending
head = [861, 866, 868]
rest = [i for i in range(855, 937) if i not in head]
order = head + rest
order_str = ','.join(str(i) for i in order)
text, n = re.subn(r'const NEW_ORDER = \[\];',
                  f'const NEW_ORDER = [{order_str}];', text)

open('index.html', 'w', encoding='utf-8', newline='').write(text)
print(f'genre reverted to new: {reverted}')
print(f'extraGenres removed: {extra_removed}')
print(f'NEW_ORDER restored: {n} ({len(order)} ids)')
