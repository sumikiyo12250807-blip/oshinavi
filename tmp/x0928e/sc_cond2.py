import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8')
R = 'C:/Users/user/oshinavi/tmp/x0928e/'
sel = json.load(open(R + 'sc_sel.json', encoding='utf-8'))
out = open(R + 'sc_cond2.txt', 'w', encoding='utf-8')
def dump(slug):
    L = open(R + 'sc_txt/' + slug + '.txt', encoding='utf-8').read().split('\n')
    a = L.index('概要', L.index('ログアウト'))
    b = L.index('販売元', a) if '販売元' in L[a:a+60] else a + 12
    c = max(i for i, x in enumerate(L) if x == '受付・チケット情報')
    e = L.index('同じ会場のイベントを検索', c) if '同じ会場のイベントを検索' in L[c:] else len(L)
    out.write(f'  ### {slug} :: ' + ' / '.join(x for x in L[a+1:b] if not x.startswith('〒') and 'マップ' not in x) + '\n')
    rec = [i for i in range(c, e) if L[i] == '販売受付期間']
    for k, i in enumerate(rec):
        nxt = rec[k+1] if k + 1 < len(rec) else e
        # ticket types: line followed by a status-ish line and then price
        tt = []
        for j in range(i + 3, nxt - 3):
            if re.match(r'^¥[\d,]+', L[j]) or L[j] == '無料':
                # look back for name/status
                st = L[j-1] if L[j-1] != '分配不可' else L[j-2]
                tt.append(st)
        from collections import Counter
        out.write(f'   R[{L[i-3]}|{L[i-2]}] {L[i-1]} :: {L[i+1]} {L[i+2]} :: types={dict(Counter(tt))}\n')
    if not rec:
        out.write('   (no 販売受付期間) ' + ' | '.join(L[c+1:c+15]) + '\n')
for s in sel:
    e = s['entry']
    out.write(f"==== {s['src']} {s['key']} date={e.get('date')} label={e.get('dateLabel')} venue={e.get('venue')} pref={e.get('prefecture')} :: {e.get('name')[:40]}\n")
    for t in e.get('tickets', []):
        out.write('  T ' + json.dumps({k: v for k, v in t.items() if k not in ('url', 'soldoutSince')}, ensure_ascii=False) + ' @' + t.get('url', '').split('/e/')[-1] + '\n')
    urls = []
    for u in [e['links']['livepocket']] + [t.get('url') for t in e.get('tickets', [])]:
        if u and u not in urls: urls.append(u)
    for u in urls:
        dump(u.rstrip('/').split('/e/')[1])
