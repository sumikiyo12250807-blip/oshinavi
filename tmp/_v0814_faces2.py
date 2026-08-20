import re, json, sys, os, glob
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\user\oshinavi')
h = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
byid = {e['id']: e for e in ev}
so_ids = [e['id'] for e in ev if any(t.get('soldout') for t in (e.get('tickets') or []))]
ssr = h[h.index('<!-- AI_SSR_START -->'):h.index('<!-- AI_SSR_END -->')]
ai = {f: open(f, encoding='utf-8', newline='').read() for f in sorted(glob.glob('ai_*.html'))}
if os.path.exists('ai.html'): ai['ai.html'] = open('ai.html', encoding='utf-8', newline='').read()

print("### SSR で 予定枚数終了 が付いてる行:")
for m in re.finditer(r'<li>⚫[^<]*予定枚数終了[^\n]*', ssr):
    print("  ", m.group(0)[:150])

print("\n### ai*.html で 予定枚数終了 を含む行:")
cnt = 0
for f, txt in ai.items():
    for line in txt.split('\n'):
        if '予定枚数終了' in line:
            cnt += 1
            print("  [%s] %s" % (f, line.strip()[:170]))
print("  合計:", cnt)

print("\n### 名前ベースで3面照合")
for i in so_ids:
    e = byid[i]
    nm = (e.get('name') or e.get('artist') or '')
    inssr = any(nm in m.group(0) for m in re.finditer(r'<li>[^\n]*', ssr) if '予定枚数終了' in m.group(0))
    inai = any(('予定枚数終了' in line and nm in line) for txt in ai.values() for line in txt.split('\n'))
    print("  id%-5s ssr⚫=%-5s ai⚫=%-5s %s" % (i, inssr, inai, nm[:40]))
