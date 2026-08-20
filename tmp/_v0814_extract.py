import re, json, sys, io, collections
sys.stdout.reconfigure(encoding='utf-8')

P = r'C:\Users\user\oshinavi\index.html'
h = open(P, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
ev = json.loads(m.group(2))
print("EVENTS件数:", len(ev))

# NEW_ORDER
mo = re.search(r'const NEW_ORDER\s*=\s*(\[.*?\])\s*;', h, re.S)
if mo:
    try:
        no = json.loads(mo.group(1))
        print("NEW_ORDER件数:", len(no), "中身:", no[:20])
    except Exception as e:
        print("NEW_ORDER parse fail:", e, mo.group(1)[:200])
else:
    print("NEW_ORDER 見つからず")

# genre == new
newg = [e for e in ev if e.get('genre') == 'new']
print("genre==new 件数:", len(newg), [e.get('id') for e in newg][:30])

# draft fields
draft = [e for e in ev if ('_genre' in e or '_piaSub' in e)]
print("_genre/_piaSub 残存 件数:", len(draft))
print("  うち id4226-4275:", sorted([e['id'] for e in draft if 4226 <= e.get('id',0) <= 4275]))
print("  全部のid:", sorted([e['id'] for e in draft])[:80])

# soldout
so = []
for e in ev:
    for t in (e.get('tickets') or []):
        if t.get('soldout') is True:
            so.append((e['id'], e.get('title'), t.get('type'), t.get('date'), t.get('startDate'), t.get('soldoutSince')))
print("soldout券種 数:", len(so))
ids = sorted(set(x[0] for x in so))
print("soldoutを持つエントリ数:", len(ids), ids)
for x in so:
    print("  SO", x)

# CRLF check
raw = open(P, 'rb').read()
lone_lf = len(re.findall(rb'(?<!\r)\n', raw))
print("CRLF数:", raw.count(b'\r\n'), "単独LF数:", lone_lf)

# target ids
for tid in [2789, 3153, 3316, 3699, 3927]:
    e = next((x for x in ev if x.get('id') == tid), None)
    if not e:
        print(f"--- id{tid}: 見つからず")
        continue
    print(f"--- id{tid} {e.get('title')} genre={e.get('genre')} date={e.get('date')} pref={e.get('prefecture')} area={e.get('area')} venue={e.get('venue')}")
    print("    links:", json.dumps(e.get('links'), ensure_ascii=False))
    for t in (e.get('tickets') or []):
        print("    T:", json.dumps(t, ensure_ascii=False))
