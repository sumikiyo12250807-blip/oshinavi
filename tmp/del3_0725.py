import json, re, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

IDS = {1350, 1357, 1695, 2082, 2129, 2779, 2929}

path = 'index.html'
h = open(path, encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))

bak = 'index.html.bak_0725_noon_delete'
shutil.copyfile(path, bak)

keep, gone = [], []
for e in EV:
    (gone if e.get('id') in IDS else keep).append(e)

missing = IDS - {e.get('id') for e in gone}
if missing:
    print('!! 見つからないid:', sorted(missing))

new_arr = json.dumps(keep, ensure_ascii=False, indent=2)
open(path, 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])

print('backup:', bak)
print('削除 %d件 / %d → %d件' % (len(gone), len(EV), len(keep)))
for e in gone:
    print('  -', e.get('name'), '(公演日 %s)' % e.get('date'))
