# -*- coding: utf-8 -*-
# TicketDive（すちこ 11/12「新着の上の方に並べて」）：番人 → 投入（鍵）→ 新着の並び（NEW_ORDER）の先頭へ → 番人 --ids → commit
import io, json, os, re, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1124/td/'
os.makedirs(D, exist_ok=True)
while not os.path.exists('tmp/x1123/night_chain23.done'):
    time.sleep(60)
LK = 'tmp/x1112/index.lock'
log = io.open(D + 'td_inject.txt', 'w', encoding='utf-8')
def W(m):
    log.write(m + '\n'); log.flush()
def run(a, keep=2500):
    r = subprocess.run([sys.executable] + a, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    W('=== %s rc=%d %s\n%s\n%s' % (' '.join(a)[:90], r.returncode, time.strftime('%H:%M:%S'), r.stdout[-keep:], r.stderr[-500:]))
    return r
def lock():
    while True:
        try:
            fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'td24'); os.close(fd); return
        except FileExistsError:
            time.sleep(10)
# 朝の組み上がりは古くなる（発売が始まった受付）＝いまの売り場から集め直して組み直す
run(['tools/ticketdive_harvest.py', '--out', D + 'harvest2.json'], 800)
run(['tools/build_ticketdive_entries.py', D + 'harvest2.json', '--out', D + 'built.json'], 800)
g = run(['tools/gate_ticketdive_slots.py', '--built', D + 'built.json'])
if g.returncode != 0:
    W('番人が鳴った＝投入しない'); log.close(); io.open(D + 'done', 'w').write('gate'); sys.exit(1)
def ids_td():
    s = io.open('index.html', encoding='utf-8').read()
    i = s.index('const EVENTS = [') + len('const EVENTS = ')
    E, _ = json.JSONDecoder().raw_decode(s[i:])
    return {e['id'] for e in E if e.get('genre') == 'new' and 'ticketdive.com' in json.dumps(e.get('links') or {}) + json.dumps(e.get('tickets') or [])}
before = ids_td()
lock()
try:
    run(['tools/inject_ticketdive.py', D + 'built.json', '--apply'])
    new = sorted(ids_td() - before)
    W('入れた %d件 %s〜%s' % (len(new), new[:1], new[-1:]))
    t = io.open('index.html', encoding='utf-8', newline='').read()
    mo = re.search(r'NEW_ORDER\s*=\s*\[([^\]]*)\]', t)
    cur = [x.strip() for x in mo.group(1).split(',') if x.strip()]
    ns = [str(x) for x in new]
    order = ns + [x for x in cur if x not in set(ns)]
    t = t[:mo.start(1)] + ','.join(order) + t[mo.end(1):]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(t)
    W('NEW_ORDER 先頭へ %d件・全体 %d' % (len(ns), len(order)))
    json.dump(new, io.open(D + 'td_new_ids.json', 'w'))
finally:
    os.remove(LK)
if new:
    run(['tools/gate_ticketdive_slots.py', '--ids', ','.join(map(str, new))])
io.open(D + 'msg.txt', 'w', encoding='utf-8').write(
    '11/24 朝（commit だけ）：すちこ「これはこれで全部なの？」＝TicketDive を上限なし（前は100公演で打ち切り）で集め直して新着の先頭へ＝番人 → inject_ticketdive --apply %d件\n\n'
    'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n'
    'Claude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n' % len(new))
run(['tmp/x1112/commit.py', D + 'msg.txt'])
W('終わり')
io.open(D + 'done', 'w').write('ok')
log.close()
