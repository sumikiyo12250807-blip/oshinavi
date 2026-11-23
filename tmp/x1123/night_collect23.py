# -*- coding: utf-8 -*-
# 11/21 夜：①新着の振り分け（assign_night15）→ ②収集＝ぴあ 発売前（7ジャンル×0102/0202）を引き直し、今朝より後に出た未登録を
#   組み立て（50件ずつ）→ 鍵 → 新着へ（eventCd で二重を外す）→ reconcile_pia --ids → gate_fields → HEAD比べ → commit（push しない）
#   ぴあは1本ずつ＝この1本に並べる。e+ は夜通しの収集（overnight_1115）が受け持つ
import io, json, glob, os, re, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1123/'
O = D + 'night_pia/'
os.makedirs(O, exist_ok=True)
LK = 'tmp/x1112/index.lock'
log = io.open(O + 'night_pia.txt', 'a', encoding='utf-8')
def W(m):
    log.write(time.strftime('%H:%M ') + m + '\n'); log.flush()
def run(a, out, timeout=None):
    r = subprocess.run([sys.executable] + a, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env, timeout=timeout)
    io.open(O + out, 'w', encoding='utf-8').write('rc=%d\n%s\n--stderr--\n%s' % (r.returncode, r.stdout[-30000:], r.stderr[-6000:]))
    W('%s rc=%d %s' % (' '.join(a)[:70], r.returncode, ' | '.join(l for l in r.stdout.splitlines() if l.startswith('===') or '集計' in l)[:400]))
    return r
def lock():
    while True:
        try:
            fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'night_pia'); os.close(fd); return
        except FileExistsError:
            time.sleep(20)
def unlock():
    try:
        os.remove(LK)
    except FileNotFoundError:
        pass
def count():
    s = io.open('index.html', encoding='utf-8').read()
    i = s.index('const EVENTS = [') + len('const EVENTS = ')
    E, _ = json.JSONDecoder().raw_decode(s[i:])
    return len(E), sum(1 for e in E if e.get('genre') == 'new')

# ① 振り分け
W('振り分けは夕方の鎖（assign22n）で済み')
W('収集はじめ カード=%d 新着=%d' % count())
# ② ぴあ 発売前の引き直し
for lg in ['01', '02', '07', '06', '03', '04', '05']:
    for st in ['0102', '0202']:
        f = O + 'presale_%s_%s.json' % (lg, st)
        if not os.path.exists(f):
            run(['tools/presale_harvest.py', lg, f, 'rlsStatus=%s' % st], 'sweep_%s_%s.txt' % (lg, st))
s = io.open('index.html', encoding='utf-8').read()
have = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', s))
seen, cands = set(), []
for f in sorted(glob.glob(O + 'presale_*.json')):
    try:
        d = json.load(io.open(f, encoding='utf-8'))
    except Exception:
        continue
    for it in (d.get('new') or []):
        u = it.get('url') or ''
        cd = re.findall(r'event(?:Bundle)?Cd=(\w+)', u)
        if not cd or cd[0] in have or u in seen:
            continue
        seen.add(u)
        cands.append({'newid': 960000 + len(cands), 'artist': it.get('artist') or '', 'urls': [u]})
json.dump(cands, io.open(O + 'pia_cands.json', 'w', encoding='utf-8'), ensure_ascii=False)
W('ぴあ候補（未登録） %d' % len(cands))
built, gone = [], []
for k in range(0, len(cands), 50):
    part = cands[k:k + 50]
    b = None
    for t in range(6):
        pf = O + 'pia_cands_%03d.json' % k
        json.dump(part, io.open(pf, 'w', encoding='utf-8'), ensure_ascii=False)
        r = subprocess.run([sys.executable, 'tools/build_pia_entries.py', pf], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env, timeout=3600)
        io.open(O + 'pia_build_err_%03d.txt' % k, 'w', encoding='utf-8').write(r.stderr[-30000:])
        try:
            b = [x for x in json.loads(r.stdout) if x.get('tickets')]
            break
        except Exception as ex:
            mg = re.search(r'PiaEventGone.*?(https://\S+eventCd=\w+)', r.stderr)
            if mg:
                gone.append(mg.group(1)); part = [c for c in part if mg.group(1) not in c['urls']]
                W('組 %d 消えたURLを外す %s' % (k, mg.group(1))); continue
            W('組 %d 失敗 %d回目 %s' % (k, t + 1, ex)); time.sleep(300)
    b = b or []
    built += b
    W('組み立て %d〜 → 枠あり %d' % (k, len(b)))
json.dump(built, io.open(O + 'pia_built.json', 'w', encoding='utf-8'), ensure_ascii=False)
new_ids = []
if built:
    lock()
    try:
        text = io.open('index.html', encoding='utf-8', newline='').read()
        m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
        st = m.start(1)
        E, end = json.JSONDecoder().raw_decode(text, st)
        reg = text[st:end]
        nid = max(e['id'] for e in E) + 1
        for b in built:
            cds = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', json.dumps(b)))
            if cds and any(('Cd=' + c) in reg for c in cds):
                continue
            b['id'] = nid; b['genre'] = 'new'; nid += 1
            E.append(b); new_ids.append(b['id'])
            reg += json.dumps(b)
        if new_ids:
            body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E) + '\n]'
            text = text[:st] + body.replace('\n', '\r\n') + text[end:]
            mo = re.search(r'NEW_ORDER\s*=\s*\[([^\]]*)\]', text)
            ids = [x.strip() for x in mo.group(1).split(',') if x.strip()] + [str(x) for x in new_ids]
            text = text[:mo.start(1)] + ','.join(ids) + text[mo.end(1):]
            io.open('index.html', 'wb').write(text.encode('utf-8'))
    finally:
        unlock()
json.dump(new_ids, io.open(O + 'pia_new_ids.json', 'w'))
W('ぴあ 新着に入れた %d（%s〜%s）' % (len(new_ids), new_ids[:1], new_ids[-1:]))
if new_ids:
    run(['tools/reconcile_pia.py', '--ids', ','.join(map(str, new_ids))], 'pia_rec.txt', timeout=7200)
    run(['tools/gate_fields.py'], 'gate_fields_pia.txt')
    run(['tmp/heal_head_compare_1805.py'], 'hc_pia.txt')
    io.open(O + 'msg.txt', 'w', encoding='utf-8').write(
        '11/23 夜（commit だけ）：ぴあ 発売前（7ジャンル×0102/0202）を引き直し、今朝より後に出た未登録 %d件を組み立てて新着へ → reconcile_pia --ids・gate_fields・HEAD比べ（振り分けは明朝の照合のあと）\n\n'
        'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n' % len(new_ids))
    run(['tmp/x1112/commit.py', O + 'msg.txt'], 'commit.txt')
W('おわり カード=%d 新着=%d' % count())
io.open(O + 'night_pia.done', 'w').write(str(len(new_ids)))
