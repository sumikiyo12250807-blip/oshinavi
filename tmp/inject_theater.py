import json, re

entries = json.load(open('tmp/theater_entries.json', encoding='utf-8'))
# extract _genre into table, strip from entries
gt_lines = []
for e in entries:
    g = e.pop('_genre', 'engeki')
    e['genre'] = 'new'
    gt_lines.append(f"{e['id']}\t{g}\t{e.get('name','')}")
open('tmp/genre_table_theater.tsv','w',encoding='utf-8').write('\n'.join(gt_lines)+'\n')

src = open('index.html', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
text = src.replace('\r\n','\n')

# locate EVENTS array bounds
i0 = text.index('const EVENTS = [')
br = text.index('[', i0)
depth=0; i=br
while i < len(text):
    c=text[i]
    if c=='[': depth+=1
    elif c==']':
        depth-=1
        if depth==0: break
    i+=1
ci = i  # closing ] of EVENTS

# format new entries: indent each by 2 spaces (object brace at 2, fields at 4)
def fmt(e):
    s = json.dumps(e, ensure_ascii=False, indent=2)
    return '\n'.join('  '+ln for ln in s.split('\n'))
block = ',\n'.join(fmt(e) for e in entries)

head = text[:ci].rstrip()   # ends with last entry '}'
tail = text[ci:]            # '];...'
newtext = head + ',\n' + block + '\n' + tail

# update NEW_ORDER
ids = [e['id'] for e in entries]
newtext = re.sub(r'const NEW_ORDER = \[\];',
                 'const NEW_ORDER = ['+','.join(str(x) for x in ids)+'];',
                 newtext)

open('index.html','w',encoding='utf-8',newline='').write(newtext.replace('\n', nl))
print('injected', len(entries), 'entries')
