import re, json, sys, os, glob
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\user\oshinavi')
h = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
byid = {e['id']: e for e in ev}
so_ids = [e['id'] for e in ev if any(t.get('soldout') for t in (e.get('tickets') or []))]

# --- SSR block
ssr = h[h.index('<!-- AI_SSR_START -->'):h.index('<!-- AI_SSR_END -->')]
print("SSR <li>数:", ssr.count('<li>'))
print("SSR 予定枚数終了 出現:", ssr.count('予定枚数終了'))
# ai*.html
ai_all = ''
files = sorted(glob.glob('ai_*.html')) + (['ai.html'] if os.path.exists('ai.html') else [])
for f in files:
    ai_all += open(f, encoding='utf-8', newline='').read()
print("ai*.html 数:", len(files), " 予定枚数終了 出現:", ai_all.count('予定枚数終了'))

# per-entry presence using pia URL as key
miss = []
for i in so_ids:
    e = byid[i]
    url = (e.get('links') or {}).get('pia') or ''
    key = url.split('=')[-1] if url else str(i)
    name = (e.get('name') or e.get('artist') or '')
    in_ssr = key in ssr
    in_ai = key in ai_all
    # is the soldout marker attached in each face?
    def near(text):
        for m in re.finditer(re.escape(key), text):
            seg = text[max(0, m.start()-900):m.start()+200]
            li = seg.rfind('<li>')
            if li >= 0 and '予定枚数終了' in seg[li:]:
                return True
        return False
    ssr_mark = near(ssr); ai_mark = near(ai_all)
    ok = ssr_mark and ai_mark
    print("id%-5s ssr掲載=%-5s ssr⚫=%-5s ai掲載=%-5s ai⚫=%-5s  %s" % (i, in_ssr, ssr_mark, in_ai, ai_mark, name[:34]))
    if not ok:
        miss.append((i, name, in_ssr, ssr_mark, in_ai, ai_mark))

print("\n3面不整合:", len(miss))
for m in miss: print("  ", m)

# --- renderCard 側のロジック抜粋
js = h
for kw in ['予定枚数終了', 'soldout']:
    print("\n--- index.html 内 '%s' 出現位置(JS部分)" % kw)
    for m in list(re.finditer(kw, js))[:60]:
        seg = js[max(0,m.start()-140):m.start()+140].replace('\r\n',' ⏎ ')
        if 'AI_SSR' in seg or seg.strip().startswith('<li>'): continue
        print("   ...", seg[:280])
        break
