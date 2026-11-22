# -*- coding: utf-8 -*-
# 朝の削除：check_expired と独立再導出（「削除は誤りという前提で」）が一致した分だけ。割れた分は残す
# 使い方: python del_apply.py [--apply]
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
root = 'C:/Users/user/oshinavi/'
CUT = '2026-11-21'
APPLY = '--apply' in sys.argv
a = json.load(io.open(root + 'tmp/x1122/expired.json', encoding='utf-8'))
mine = set(a['全販売終了, 開催終了#']) | set(a.get('del', []))
R = json.load(io.open(root + 'tmp/x1122/agent_del/result.json', encoding='utf-8'))
theirs = set(int(x) for x in R['delete'])
keep = R.get('keep') or {}
ids = mine & theirs
print(f'候補 {len(mine)} / 独立 {len(theirs)} / 一致 {len(ids)} / 候補だけ {len(mine - theirs)} / 独立だけ {len(theirs - mine)}')
for i in sorted(mine - theirs):
    print('  候補だけ', i, keep.get(str(i), ''))
print('  独立だけ', sorted(theirs - mine))
if not APPLY:
    sys.exit(0)
import os, time, atexit
LK = root + 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'del_apply22'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
atexit.register(lambda: os.path.exists(LK) and os.remove(LK))
text =io.open(root + 'index.html', encoding='utf-8', newline='').read()
io.open(root + 'index.html.bak_1122_del', 'w', encoding='utf-8', newline='').write(text)
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
st = m.start(1)
E, end = json.JSONDecoder().raw_decode(text, st)
gone = sorted((e for e in E if e['id'] in ids), key=lambda e: (e.get('date', ''), e['id']))
assert len(gone) == len(ids), (len(gone), len(ids))
assert all(e.get('date', '9') <= CUT for e in gone)
for e in gone:
    for t in e.get('tickets') or []:
        assert (t.get('date') or '') <= CUT or t.get('soldout'), (e['id'], t)
E = [x for x in E if x['id'] not in ids]
body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E) + '\n]'
text = text[:st] + body.replace('\n', '\r\n') + text[end:]
mo = re.search(r'NEW_ORDER\s*=\s*\[([^\]]*)\]', text)
kp = [x.strip() for x in mo.group(1).split(',') if x.strip() and int(x.strip()) not in ids]
text = text[:mo.start(1)] + ','.join(kp) + text[mo.end(1):]
io.open(root + 'index.html', 'wb').write(text.encode('utf-8'))
L = ['', f'## 2026-11-22 夕方（遅れた朝の分）で削除したエントリ（期限切れ） {len(gone)}件', '',
     f'理由＝**公演日が過ぎた**（買える枠も1つも残っていない）。check_expired の候補{len(mine)}件と、別エージェントの独立再導出（「削除は誤りという前提で」）の{len(theirs)}件が一致した分だけ。',
     f'残したもの＝割れた{len(mine - theirs)}件', '']
for e in gone:
    L.append(f"- id={e['id']} {e.get('name') or e.get('artist')} ／ （公演 {e.get('date','')}）")
    us = []
    for t in e.get('tickets') or []:
        u = t.get('url')
        if u and u not in us: us.append(u)
    for v in (e.get('links') or {}).values():
        if v and 'amazon' not in v and v not in us: us.append(v)
    for u in us[:3]:
        L.append(f'  - {u}')
io.open(root + 'logs/removed_2026-11-22.md', 'a', encoding='utf-8').write('\n'.join(L) + '\n')
print(f'消した {len(gone)} / new_order {len(kp)}')
print('crlf', text.count('\r\n'), 'lf_only', text.count('\n') - text.count('\r\n'))
