# -*- coding: utf-8 -*-
"""夜の突き合わせで足した18枠に、取り直し元のぴあURLを焼き込む＋二重に入った双子を外す。

🚨build_pia_entries は ticket.url を付けないことがある。空のまま出すと
   押しても飛べないバッジになる（[[feedback_tour_per_ticket_url]]）。
使い方: python tmp/x0920/stamp_gap.py [--apply]
"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
NL = '\r\n'

url_of = {c['newid']: c['urls'][0]
          for c in json.load(io.open('tmp/x0920/cands_gap.json', encoding='utf-8'))}
t = io.open('tmp/x0920/built_gap.json', encoding='utf-8', errors='replace').read()
src = {}
for e in json.loads(t[t.find('['):]):
    u = url_of.get(e['id'])
    for tk in (e.get('tickets') or []):
        src[(e['id'], tk.get('type'), tk.get('date'))] = u

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

fixed, dropped = 0, []
for e in EVENTS:
    ts = e.get('tickets') or []
    seen, keep = set(), []
    withurl = {(x.get('type'), x.get('date')) for x in ts if x.get('url')}
    for tk in ts:
        k = (e['id'], tk.get('type'), tk.get('date'))
        kk = (tk.get('type'), tk.get('date'), tk.get('url'))
        if kk in seen:                      # 全く同じ枠が2つ＝双子
            dropped.append((e['id'], (tk.get('type') or '')[:46]))
            continue
        seen.add(kk)
        if (not tk.get('url')) and k in src and (tk.get('type'), tk.get('date')) in withurl:
            dropped.append((e['id'], (tk.get('type') or '')[:46]))
            continue
        if (not tk.get('url')) and k in src and src[k]:
            fixed += 1
            if APPLY:
                tk['url'] = src[k]
        keep.append(tk)
    if APPLY:
        e['tickets'] = keep

print('今夜足した枠 %d / 飛び先を焼く %d / 双子を外す %d' % (len(src), fixed, len(dropped)))
for d in dropped[:10]:
    print('  − id%s %s' % d)
if not APPLY:
    print('(--apply で書き込み)')
    sys.exit(0)

io.open('index.html.bak_0920_stampgap', 'w', encoding='utf-8', newline='').write(h)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1)
    + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
    + m.group(3) + h[m.end():])
raw = io.open('index.html', 'rb').read()
assert raw.count(b'\r\r\n') == 0 and not re.findall(rb'(?<!\r)\n', raw), '改行が壊れた'
print('書き込み完了（バックアップ index.html.bak_0920_stampgap）')
