import re, json, sys, os, subprocess, difflib, glob
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\user\oshinavi')

def strip_events(text):
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', text, re.S)
    a = text[:m.start(2)] + '<<EVENTS>>' + text[m.end(2):]
    # SSRブロックも除く（データ由来なので）
    s, e = a.index('<!-- AI_SSR_START -->'), a.index('<!-- AI_SSR_END -->')
    return a[:s] + '<<SSR>>' + a[e:]

old = subprocess.run(['git','show','6f73da7:index.html'], capture_output=True).stdout.decode('utf-8')
new = open('index.html', encoding='utf-8', newline='').read()
a, b = strip_events(old).replace('\r\n','\n').split('\n'), strip_events(new).replace('\r\n','\n').split('\n')
d = [l for l in difflib.unified_diff(a, b, lineterm='', n=0) if l[:1] in '+-' and l[:3] not in ('+++','---')]
print("■ EVENTS/SSRを除いた index.html の差分 %d行（6f73da7→現在）" % len(d))
for l in d: print("   ", l[:190])

print("\n■ 並び順に関わる関数の同一性チェック")
for name, pat in [('ticketSortKey', r'const ticketSortKey = \(t\) => \{.*?\};'),
                  ('saleStartPending', r'function saleStartPending\(t\) \{.*?\n  \}'),
                  ('EVENTS.sort', r'\.sort\(\(a, ?b\) => \{.*?\}\)'),
                  ('sortKey', r'function sortKey\(.*?\n  \}')]:
    ao = re.findall(pat, old, re.S); bo = re.findall(pat, new, re.S)
    same = ao == bo
    print("   %-18s 旧%d件 新%d件 同一=%s" % (name, len(ao), len(bo), same))
    if not same:
        for x, y in zip(ao, bo):
            if x != y:
                print("     旧:", x[:300]); print("     新:", y[:300])

print("\n■ 3面の件数")
h = new
ssr = h[h.index('<!-- AI_SSR_START -->'):h.index('<!-- AI_SSR_END -->')]
print("   SSR: li=%d / ⚫予定枚数終了=%d / ⚪販売終了=%d" % (ssr.count('<li>'), ssr.count('⚫ 予定枚数終了'), ssr.count('⚪ 販売終了')))
ai = ''.join(open(f, encoding='utf-8', newline='').read() for f in sorted(glob.glob('ai_*.html')))
print("   ai*: ⚫予定枚数終了=%d / ⚪販売終了=%d" % (ai.count('⚫ 予定枚数終了'), ai.count('⚪ 販売終了')))
ev = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
ent_sold = [e for e in ev if any(t.get('soldout') and not t.get('saleEnded') for t in (e.get('tickets') or []))]
ent_se_only = [e for e in ev if any(t.get('soldout') for t in (e.get('tickets') or []))
               and not any(t.get('soldout') and not t.get('saleEnded') for t in (e.get('tickets') or []))]
print("   データ: ⚫になるべきエントリ=%d / ⚪になるべきエントリ=%d" % (len(ent_sold), len(ent_se_only)))
print("   ⚪になるべき:", [e['id'] for e in ent_se_only])
# renderCard 枠単位
n_sold = sum(1 for e in ev for t in (e.get('tickets') or []) if t.get('soldout') and not t.get('saleEnded'))
n_se = sum(1 for e in ev for t in (e.get('tickets') or []) if t.get('saleEnded'))
print("   renderCard 枠単位: 予定枚数終了=%d / 販売終了=%d" % (n_sold, n_se))
