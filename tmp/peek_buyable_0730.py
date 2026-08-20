"""指定idについて、ぴあ側の「買える枠」と登録枠を並べてUTF-8ファイルに出す。
reconcile_pia の内部関数をそのまま使う＝ゲートと同じ見え方を確認するため。"""
import json
import re
import sys

sys.path.insert(0, 'tools')
import reconcile_pia as R

IDS = [3372, 3398]

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

out = []
for i in IDS:
    e = byid[i]
    urls = R.pia_urls(e)
    out.append(f"id={i}  {e.get('artist')}")
    out.append(f"  venue={e.get('venue')}  ev.date={e.get('date')}")
    out.append(f"  dateLabel={e.get('dateLabel')}")
    for u in urls:
        out.append(f"  URL: {u}")
    out.append('  --- 登録tickets ---')
    for t in e.get('tickets') or []:
        out.append(f"    type={t.get('type')}")
        out.append(f"      date={t.get('date')} startDate={t.get('startDate')} url={t.get('url') or '-'}")
    buyable, drops, errs, tries = R.fetch_buyable(urls, len(e.get('tickets') or []))
    out.append('  --- ぴあ側の買える枠 ---')
    for b in buyable:
        out.append(f"    [{b['state']}] {b['suf']}  iso={b['iso']} sd={b.get('sd')}")
        out.append(f"      title={b['title']}")
        out.append(f"      prefs={b.get('prefs')} perfdate={b.get('perfdate')} perf_end={b.get('perf_end')}")
    if drops:
        out.append('  --- DROP(解析不能) ---')
        for d in drops:
            out.append(f"    {d}")
    if errs:
        out.append(f'  --- FETCH失敗 --- {errs}')
    out.append('')

open('tmp/peek_buyable_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/peek_buyable_0730.txt')
