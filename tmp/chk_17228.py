import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
s = open(r'C:\Users\user\oshinavi\index.html', encoding='utf-8').read()
for i in range(17228, 17234):
    m = re.search(r'\{\s*"?id"?\s*:\s*"?%d"?\s*,' % i, s)
    if not m:
        print(i, 'NOT FOUND'); continue
    st = m.start(); depth = 0; j = st
    while True:
        c = s[j]
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: break
        j += 1
    blk = s[st:j+1]
    name = re.search(r'"?name"?\s*:\s*"([^"]*)"', blk)
    genre = re.search(r'"?genre"?\s*:\s*"([^"]*)"', blk)
    urls = sorted(set(re.findall(r'https?://[^"\s]*pia[^"\s]*', blk)))
    print(i, name.group(1) if name else '', genre.group(1) if genre else '')
    for u in urls: print('   ', u)
m = re.findall(r'class="filter-btn[^"]*"[^>]*data-genre="([^"]+)"[^>]*>([^<]*)<', s)
print('GENRES', m)
