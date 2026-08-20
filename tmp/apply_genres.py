import re

# id -> genre from table
genre_map = {}
for line in open('tmp/genre_table.tsv', encoding='utf-8').read().splitlines():
    if not line.strip():
        continue
    i, g, name = line.split('\t')
    genre_map[int(i)] = g

# borderline overrides: id -> (main_genre, [extra])
override = {
    899: ('jpop', ['hiphop']),
    922: ('jpop', ['rock']),
    903: ('rock', ['fes']),
    907: ('rock', ['fes']),
}
for i, (mg, ex) in override.items():
    genre_map[i] = mg

lines = open('index.html', encoding='utf-8', newline='').read().split('\r\n')
out = []
cur_id = None
applied = 0
extra_applied = 0
id_re = re.compile(r'^\s*"id":\s*(\d+),')
for ln in lines:
    m = id_re.match(ln)
    if m:
        cur_id = int(m.group(1))
    # genre:"new" line
    if ln.strip().startswith('"genre": "new"'):
        if cur_id in genre_map:
            indent = ln[:len(ln) - len(ln.lstrip())]
            new_g = genre_map[cur_id]
            # preserve trailing comma
            comma = ',' if ln.rstrip().endswith(',') else ''
            out.append(f'{indent}"genre": "{new_g}"{comma}')
            applied += 1
            if cur_id in override:
                ex = override[cur_id][1]
                ex_str = ', '.join(f'"{e}"' for e in ex)
                out.append(f'{indent}"extraGenres": [{ex_str}],')
                extra_applied += 1
            continue
    out.append(ln)

open('index.html', 'w', encoding='utf-8', newline='').write('\r\n'.join(out))
print(f'genre applied: {applied}')
print(f'extraGenres added: {extra_applied}')
