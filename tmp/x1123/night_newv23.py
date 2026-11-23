# -*- coding: utf-8 -*-
# 11/23 夜通し すちこ「振り分けと夜通し頼みます　新しい売り場からもお願いね」
#  新しい売り場5つ（宝塚・松竹・TicketRugby・チケットボード・B.LEAGUE）を1本ずつ順に：
#   ① 集める → 組み立て → 番人 --built（🚨❌ℹ️ の並び番号を外す）→ 鍵 → inject --apply（登録済みは道具が外す）
#   ② 登録済みも番人 → 鳴った分を heal --apply（鍵）→ 番人 --ids でもう一度
#  → 全部のあと HEAD比べ・gate_fields → commit → 新しい売り場の新着を振り分け（assign_newv20 の夜版・R は止めない）
#  段ごとに .done（止まっても続きから）
import io, json, os, re, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1123/newv_n/'
os.makedirs(D, exist_ok=True)
LK = 'tmp/x1112/index.lock'
log = io.open(D + 'log.txt', 'a', encoding='utf-8')
def W(m):
    log.write(time.strftime('%H:%M ') + m + '\n'); log.flush()
def run(a, out, timeout=3 * 3600):
    try:
        r = subprocess.run([sys.executable] + a, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env, timeout=timeout)
    except subprocess.TimeoutExpired:
        W('⏰ 時間切れ %s' % ' '.join(a)[:80]); return None
    io.open(D + out, 'w', encoding='utf-8').write('rc=%d\n%s\n--stderr--\n%s' % (r.returncode, r.stdout[-20000:], r.stderr[-4000:]))
    W('%s rc=%d %s' % (' '.join(a)[:80], r.returncode, ' | '.join((r.stdout.strip().splitlines() or [''])[-2:])[:300]))
    return r
def lock(tag):
    while True:
        try:
            fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, tag.encode()); os.close(fd); return
        except FileExistsError:
            time.sleep(15)
def unlock():
    if os.path.exists(LK):
        os.remove(LK)
V = [('takarazuka', 'takarazuka', ['--index-venue']), ('shochiku', 'shochiku', []), ('rugby', 'rugby', []),
     ('tickebo', 'tickebo', []), ('bleague', 'bleague', [])]
put = {}
for v, g, bx in V:
    O = D + v + '/'
    os.makedirs(O, exist_ok=True)
    if os.path.exists(O + 'collect.done'):
        continue
    W('── %s 集める' % v)
    r = run(['tools/%s_harvest.py' % v, '--out', O + 'harvest.json'], v + '_harvest.txt', timeout=4 * 3600)
    if r is None or r.returncode != 0 or not os.path.exists(O + 'harvest.json'):
        W('%s 集められなかった＝飛ばす' % v); io.open(O + 'collect.done', 'w').write('fail'); continue
    r = run(['tools/build_%s_entries.py' % v, O + 'harvest.json', '--out', O + 'built.json'] + bx, v + '_build.txt')
    if r is None or r.returncode != 0:
        io.open(O + 'collect.done', 'w').write('fail'); continue
    src = json.load(io.open(O + 'built.json', encoding='utf-8'))
    B = src['entries']
    run(['tools/gate_%s_slots.py' % g, '--built', O + 'built.json', '--report', O + 'gate_built.txt'], v + '_gate_built.txt', timeout=4 * 3600)
    rep = io.open(O + 'gate_built.txt', encoding='utf-8').read() if os.path.exists(O + 'gate_built.txt') else None
    if rep is None:
        W('%s 番人の報告が無い＝入れない' % v); io.open(O + 'collect.done', 'w').write('nogate'); continue
    bad = {int(x) for x in re.findall(r'(?:🚨|❌|ℹ️)[^\n]*?id=(\d+)', rep)}
    park = {i for i, e in enumerate(B) if '駐車' in (e.get('name') or '')}
    ok = [e for i, e in enumerate(B) if i not in bad and i not in park]
    src['entries'] = ok
    json.dump(src, io.open(O + 'built_ok.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    W('%s 組み立て %d ／ 番人で外す %d ／ 駐車券 %d ／ 入れる候補 %d' % (v, len(B), len(bad), len(park), len(ok)))
    if ok:
        lock('newv_n_' + v)
        try:
            r = run(['tools/inject_%s.py' % v, O + 'built_ok.json', '--apply', '--report', O + 'inject_apply.txt'], v + '_inject.txt')
            m = re.search(r'put=(\d+)', (r.stdout if r else '') or '')
            put[v] = int(m.group(1)) if m else '?'
        finally:
            unlock()
    io.open(O + 'collect.done', 'w').write(str(put.get(v, 0)))
    W('%s 新着に入れた %s' % (v, put.get(v, 0)))
for v, g, bx in V:
    O = D + v + '/'
    if os.path.exists(O + 'heal.done'):
        continue
    W('── %s 登録済みの番人' % v)
    run(['tools/gate_%s_slots.py' % g], v + '_gate_all.txt', timeout=4 * 3600)
    rep = io.open('tmp/gate_%s_report.txt' % g, encoding='utf-8').read() if os.path.exists('tmp/gate_%s_report.txt' % g) else ''
    ids = sorted({int(x) for x in re.findall(r'(?:🚨|❌)[^\n]*?id=(\d+)', rep)})
    W('%s 鳴った %d %s' % (v, len(ids), ids[:30]))
    if ids:
        lock('newv_n_heal_' + v)
        try:
            run(['tools/heal_%s.py' % g, '--ids', ','.join(map(str, ids)), '--apply'], v + '_heal.txt')
        finally:
            unlock()
        run(['tools/gate_%s_slots.py' % g, '--ids', ','.join(map(str, ids)), '--report', O + 'gate_after.txt'], v + '_gate_after.txt')
    io.open(O + 'heal.done', 'w').write(str(len(ids)))
hc = run(['tmp/heal_head_compare_1805.py'], 'hc.txt')
W('HEAD比べ ' + ((hc.stdout.strip().splitlines() or ['?'])[-1] if hc else '?'))
run(['tools/gate_fields.py'], 'gate_fields.txt')
io.open(D + 'msg.txt', 'w', encoding='utf-8').write(
    '11/23 夜通し（commit だけ）：新しい売り場5つ（宝塚・松竹・TicketRugby・チケットボード・B.LEAGUE）を集め直し（すちこ「新しい売り場からもお願いね」）＝組み立て → 番人 --built で合わない分を外して新着へ %s ／登録済みも番人 → 鳴った分を heal --apply\n\n'
    'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n' % json.dumps(put, ensure_ascii=False))
run(['tmp/x1112/commit.py', D + 'msg.txt', 'index.html'], 'commit.txt')
# 振り分け（assign_newv20 の夜版）
s = io.open('tmp/x1120/assign_newv20.py', encoding='utf-8').read()
for a, b in [("D = 'tmp/x1120/nassign_newv/'", "D = 'tmp/x1123/nassign_newv_n/'"),
             ("gfbad = {int(x) for x in re.findall(r'(?<!\\d)(\\d{4,6})(?!\\d)', gf)}",
              "gfbad = {int(x) for l in gf.splitlines() if not l.startswith('===') and not re.match(r'\\s*R\\s', l) for x in re.findall(r'(?<!\\d)(\\d{4,6})(?!\\d)', l)}"),
             ("b'assign_newv20'", "b'assign_newv_n20'"),
             ("'## 11/20 新しい売り場の振り分け", "'## 11/23 夜通し 新しい売り場の振り分け"),
             ("'11/20（commit だけ）：新しい売り場の新着を振り分け（すちこ「新着がまだまだいっぱいある」）", "'11/23 夜通し（commit だけ）：新しい売り場の新着を振り分け（すちこ「振り分けと夜通し頼みます　新しい売り場からもお願いね」）")]:
    assert a in s, a
    s = s.replace(a, b)
io.open('tmp/x1123/assign_newv_n23.py', 'w', encoding='utf-8').write(s)
run(['tmp/x1123/assign_newv_n23.py'], 'assign.txt')
W('おわり')
io.open(D + 'done', 'w').write('done')
