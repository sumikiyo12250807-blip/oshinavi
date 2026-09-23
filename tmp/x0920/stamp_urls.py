# -*- coding: utf-8 -*-
"""今朝足した枠のうち **ticket.url が空のもの**に、取り直し元のぴあURLを焼き込む（2026-09-20 朝）。

🚨なぜ＝`build_pia_entries` は ticket.url を付けないことがある。空のまま置くと
   バッジを押しても飛び先が無い＝**来た人が自分の公演に辿り着けない**
   （[[feedback_tour_per_ticket_url]]／[[feedback_build_pia_multiurl_loses_ticket_url]]）。
対象＝今朝の2回の足し込みで入れた枠だけ（元から空だった古い枠は触らない＝
   [[feedback_fix_only_what_was_pointed_at]]）。どの枠を入れたかは組み上がりJSONの
   (id, 券種名, 締切) で特定する。

使い方: python tmp/x0920/stamp_urls.py [--apply]
"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
NL = '\r\n'

# 今朝入れた枠 → 取り直し元URL
src = {}
for built_f, cand_f in (('tmp/x0920/rebuilt17.json.bak', 'tmp/x0920/alive17.txt'),
                        ('tmp/x0920/built_merge.json', 'tmp/x0920/cands_merge.json')):
    if cand_f.endswith('.txt'):
        url_of = {int(ln.split('\t')[0]): ln.split('\t')[2]
                  for ln in io.open(cand_f, encoding='utf-8').read().splitlines() if ln}
    else:
        url_of = {c['newid']: c['urls'][0] for c in json.load(io.open(cand_f, encoding='utf-8'))}
    t = io.open(built_f, encoding='utf-8', errors='replace').read()
    for e in json.loads(t[t.find('['):]):
        u = url_of.get(e['id'])
        if not u:
            continue
        for tk in (e.get('tickets') or []):
            src[(e['id'], tk.get('type'), tk.get('date'))] = u

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

fixed, dropped = 0, []
for e in EVENTS:
    ts = e.get('tickets') or []
    # 🚨今朝の足し込みで、**同じ（券種名・締切）が既にある枠の url 無しの双子**を作ってしまった。
    #   画面に同じ文字のバッジが2つ並ぶだけなので、双子のほうを外す（元の枠は触らない）。
    withurl = {(t.get('type'), t.get('date')) for t in ts if t.get('url')}
    keep = []
    for tk in ts:
        k = (e['id'], tk.get('type'), tk.get('date'))
        if (not tk.get('url')) and k in src and (tk.get('type'), tk.get('date')) in withurl:
            dropped.append((e['id'], (e.get('artist') or '')[:26], (tk.get('type') or '')[:40]))
            continue
        if (not tk.get('url')) and k in src:
            fixed += 1
            if APPLY:
                tk['url'] = src[k]
        keep.append(tk)
    if APPLY:
        e['tickets'] = keep
print('今朝入れた枠 %d / 飛び先を焼く %d / 重複の双子を外す %d' % (len(src), fixed, len(dropped)))
for d in dropped[:10]:
    print('  − id%s %s | %s' % d)
if not APPLY:
    print('(--apply で書き込み)')
    sys.exit(0)

io.open('index.html.bak_0920_stamp', 'w', encoding='utf-8', newline='').write(h)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1)
    + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
    + m.group(3) + h[m.end():])
raw = io.open('index.html', 'rb').read()
assert raw.count(b'\r\r\n') == 0 and not re.findall(rb'(?<!\r)\n', raw), '改行が壊れた'
print('書き込み完了（バックアップ index.html.bak_0920_stamp）')
