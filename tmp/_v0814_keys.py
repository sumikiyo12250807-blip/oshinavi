import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
P = r'C:\Users\user\oshinavi\index.html'
h = open(P, encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
print("keys sample:", list(ev[0].keys()))
byid = {e['id']: e for e in ev}
for tid in [2789, 3153, 3316, 3699, 3927, 130, 1071, 1149, 1487, 2223, 2265, 2300, 2341, 2401, 2415, 2416, 2815, 3287, 3432, 3513, 3651, 3766, 3872, 3875, 3912]:
    e = byid.get(tid)
    if e:
        print(tid, "|", e.get('name') or e.get('artist') or e.get('event'), "|", e.get('venue'), "|", (e.get('links') or {}).get('pia'), "|", (e.get('links') or {}).get('eplus'), "|", (e.get('links') or {}).get('rakuten') and 'rakuten有')
