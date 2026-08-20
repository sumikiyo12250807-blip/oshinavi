"""id3372/3398 をぴあから作り直して現在の登録と差分表示（--apply で適用）。
救済はヒールと同じ流儀＝tickets のみ置換（venue/dateLabel の手修正を巻き戻さない）。
CRLF保護＝読みは universal newlines、書きは text モード（newline='' 禁止）。"""
import json
import re
import sys

sys.path.insert(0, 'tools')
from build_pia_entries import build
import reconcile_pia as R

IDS = [3372, 3398]
APPLY = '--apply' in sys.argv

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

out = []
built = {}
for i in IDS:
    e = byid[i]
    urls = R.pia_urls(e)
    ne = build({'newid': i, 'artist': e.get('artist', ''), 'urls': urls})
    out.append(f"id={i}  {(e.get('artist') or '')[:60]}")
    if ne is None:
        out.append('  🚨 買える枠ゼロで返ってきた＝置換しない（要目視）')
        out.append('')
        continue
    built[i] = ne
    cur = e.get('tickets') or []
    out.append(f'  枠 {len(cur)} → {len(ne["tickets"])}')
    out.append('  --- 現在 ---')
    for t in cur:
        out.append(f"    {t.get('type')}  | date={t.get('date')} start={t.get('startDate')}")
    out.append('  --- ぴあから作り直し ---')
    for t in ne['tickets']:
        out.append(f"    {t.get('type')}  | date={t.get('date')} start={t.get('startDate')}")
    # 消える枠に非ぴあURLが無いか確認
    def key(t):
        return (t.get('type') or '', t.get('date') or '')
    newk = {key(t) for t in ne['tickets']}
    lost = [t for t in cur if key(t) not in newk]
    nonpia = [t for t in lost if t.get('url') and 'pia.jp' not in t.get('url')]
    if nonpia:
        out.append(f'  🚨 非ぴあ枠が消える {len(nonpia)}件＝適用しない方がいい')
    out.append('')

if APPLY:
    changed = 0
    for i, ne in built.items():
        byid[i]['tickets'] = ne['tickets']
        changed += 1
    open('index.html.bak_0730_rescue_pm', 'w', encoding='utf-8').write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    out.append(f'=== {changed}件 適用 (backup: index.html.bak_0730_rescue_pm) ===')
else:
    out.append('=== 表示のみ。適用するなら --apply ===')

open('tmp/rescue_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/rescue_0730.txt  apply=%s' % APPLY)
