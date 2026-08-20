import re, json, sys, subprocess, os
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\user\oshinavi')

def load(text):
    return json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', text, re.S).group(2))

def gitshow(rev):
    r = subprocess.run(['git','show',rev+':index.html'], capture_output=True)
    return r.stdout.decode('utf-8')

cur = load(open('index.html', encoding='utf-8', newline='').read())
revs = ['7219f83^','7219f83','a17e3aa','9ae6eb5','483533f','8ebfcf0','6f73da7']
prev = None
for r in revs:
    ev = load(gitshow(r))
    ids = set(e['id'] for e in ev)
    line = f"{r}: EVENTS={len(ev)}"
    if prev is not None:
        gone = sorted(prev - ids)
        add = sorted(ids - prev)
        line += f"  削除={len(gone)} 追加={len(add)}"
        if gone: line += f" 削除id={gone[:40]}"
    print(line)
    prev = ids
ids = set(e['id'] for e in cur)
gone = sorted(prev - ids); add = sorted(ids - prev)
print(f"WORKTREE: EVENTS={len(cur)} 削除={len(gone)} 追加={len(add)} 削除id={gone[:40]} 追加id={add[:40]}")

# ticket-level diff between HEAD and worktree
head = {e['id']: e for e in load(gitshow('HEAD'))}
curm = {e['id']: e for e in cur}
changed = []
for i, e in curm.items():
    h = head.get(i)
    if h is None: continue
    if json.dumps(h, ensure_ascii=False, sort_keys=True) != json.dumps(e, ensure_ascii=False, sort_keys=True):
        changed.append(i)
print("\nHEAD→worktree で変わったエントリ:", len(changed), changed)
for i in changed:
    h, e = head[i], curm[i]
    print(f"\n### id{i} {e.get('name')}")
    ht = h.get('tickets') or []; et = e.get('tickets') or []
    for k in set(list(range(max(len(ht), len(et))))):
        a = json.dumps(ht[k], ensure_ascii=False) if k < len(ht) else 'なし'
        b = json.dumps(et[k], ensure_ascii=False) if k < len(et) else 'なし'
        if a != b:
            print("  旧:", a)
            print("  新:", b)
    for f in set(h) | set(e):
        if f == 'tickets': continue
        if h.get(f) != e.get(f):
            print(f"  フィールド {f}: {h.get(f)!r} -> {e.get(f)!r}")
