# -*- coding: utf-8 -*-
"""index.html の EVENTS(JSON) から新着プール(NEW_ORDER)のエントリを取り出し、
t.pia.jp を含むもののうち id 降順12件を UTF-8 で書き出す。"""
import re, io, json, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

src = open('index.html', encoding='utf-8').read()
i = src.index('const EVENTS')
j = src.index('[', i)
depth = 0
k = j
in_str = False
esc = False
while k < len(src):
    c = src[k]
    if in_str:
        if esc:
            esc = False
        elif c == '\\':
            esc = True
        elif c == '"':
            in_str = False
    else:
        if c == '"':
            in_str = True
        elif c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                break
    k += 1
events = json.loads(src[j:k+1])
print('総エントリ数:', len(events))

m = re.search(r'const NEW_ORDER = \[([^\]]*)\]', src)
new_ids = [int(x) for x in m.group(1).split(',')]
print('NEW_ORDER 件数:', len(new_ids))

byid = {e['id']: e for e in events}
missing = [i for i in new_ids if i not in byid]
if missing:
    print('NEW_ORDERにあるがEVENTSに無いid:', missing)


def has_pia(e):
    s = json.dumps(e, ensure_ascii=False)
    return 't.pia.jp' in s


cand = [byid[i] for i in new_ids if i in byid and has_pia(byid[i])]
print('新着プールかつ t.pia.jp:', len(cand))
cand.sort(key=lambda e: -e['id'])
sel = cand[:12]

with open('tmp/audit_new_0908.json', 'w', encoding='utf-8') as f:
    json.dump(sel, f, ensure_ascii=False, indent=1)

with open('tmp/audit_new_0908.txt', 'w', encoding='utf-8') as f:
    for e in sel:
        f.write('=' * 72 + '\n')
        f.write('id=%s  %s / %s\n' % (e['id'], e.get('artist', ''), e.get('name', '')))
        f.write('  会場: %s\n' % e.get('venue', ''))
        f.write('  県: %s   公演日(date): %s\n' % (e.get('prefecture', ''), e.get('date', '')))
        f.write('  dateLabel: %s\n' % e.get('dateLabel', ''))
        f.write('  links: %s\n' % json.dumps(e.get('links', {}), ensure_ascii=False))
        ts = e.get('tickets', [])
        f.write('  枠数: %d\n' % len(ts))
        for t in ts:
            f.write('   - type=%s\n' % t.get('type', ''))
            f.write('     date(終了)=%s  startDate=%s  soldout=%s saleEnded=%s\n'
                    % (t.get('date', ''), t.get('startDate', ''), t.get('soldout'), t.get('saleEnded')))
            f.write('     dateLabel=%s\n' % t.get('dateLabel', ''))
            f.write('     url=%s\n' % t.get('url', ''))
print('書き出し完了')
