# -*- coding: utf-8 -*-
# 11/22 夕方（遅れた昼の分）の便（commit だけ）：e+ heal_eplus_started → 今日発売のぴあ heal --ids（止まった分は足し算・HEAD比べ）→ reconcile_pia --ids
#  → TIGET 21件 heal_tiget --apply → 番人 → commit
#  → e+ reconcile_eplus --third → fix_eplus_fails --apply → commit
#  → ぴあの見直し 今日の組（序数%3）→ 取りこぼしを heal --ids → commit
import io, json, os, re, shutil, subprocess, sys, time, collections, datetime
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1122/'
T = '2026-11-22'
LK = 'tmp/x1112/index.lock'
log = io.open(D + 'eve22.txt', 'a', encoding='utf-8')
def W(m):
    log.write(time.strftime('%H:%M:%S ') + m + '\n'); log.flush()
def run(a, out):
    r = subprocess.run([sys.executable] + a, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    t = r.stdout + '\n' + r.stderr
    io.open(D + out, 'w', encoding='utf-8').write('rc=%d\n%s' % (r.returncode, t))
    W('=== %s rc %d' % (' '.join(a)[:90], r.returncode))
    return t
def lock(tag):
    while True:
        try:
            fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, tag.encode()); os.close(fd); return
        except FileExistsError:
            time.sleep(15)
def unlock():
    if os.path.exists(LK):
        os.remove(LK)
def msg(name, body):
    io.open(D + name, 'w', encoding='utf-8').write(body + '\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n')
def left_today():
    s = io.open('index.html', encoding='utf-8').read()
    i = s.index('const EVENTS = [') + len('const EVENTS = ')
    E, _ = json.JSONDecoder().raw_decode(s[i:])
    by = collections.defaultdict(set)
    for e in E:
        for t in e.get('tickets') or []:
            if t.get('startDate') == T and re.search(r'\d{1,2}:\d{2}発売$', t.get('type') or ''):
                u = t.get('url') or ' '.join(x or '' for x in (e.get('links') or {}).values())
                v = 'pia' if 'pia.jp' in u else 'eplus' if 'eplus.jp' in u else 'other'
                by[v].add(e['id'])
    return by
def union_if_blocked(t, tag):
    if '🛡️' in t:
        blk = t.split('🛡️', 1)[1].split('🚨', 1)[0]
        b = re.findall(r'^\s+id=(\d+)', blk, re.M)
        if b:
            io.open('tmp/heal_blocked_hold_1805.txt', 'w', encoding='utf-8').write(','.join(b))
            W('%s 止まった %d' % (tag, len(b)))
            run(['tools/heal_union_stale.py', '--ids-src', '--apply'], 'eve22_%s_union.txt' % tag)

W('開始')
# 1) e+ 今日発売
lock('eve22_eplus')
try:
    run(['tools/heal_eplus_started.py', '--apply'], 'eve22_eplus_apply.txt')
finally:
    unlock()

pia, tg = [], []
msg('msg_eve22.txt', '11/22 夕方（commit だけ）：e+ heal_eplus_started --apply（遅れた昼の分）')
run(['tmp/x1112/commit.py', D + 'msg_eve22.txt'], 'eve22_commit.txt')

# 4) e+ 3分の1の照合
run(['tools/reconcile_eplus.py', '--third'], 'eve22_rec_eplus.txt')
lock('eve22_efix')
try:
    run(['tools/fix_eplus_fails.py', D + 'eve22_rec_eplus.txt', '--apply'], 'eve22_efix.txt')
finally:
    unlock()
msg('msg_eve22e.txt', '11/22 夕方（遅れた昼の分）（commit だけ）：reconcile_eplus --third → fix_eplus_fails --apply（売り切れ・締切ずれを e+ の実ページどおりに）')
run(['tmp/x1112/commit.py', D + 'msg_eve22e.txt'], 'eve22_commit_e.txt')

# 5) ぴあの見直し 今日の組
grp = datetime.date(2026, 11, 22).toordinal() % 3
W('ぴあの見直し 組%d 始め' % grp)
lg = 'logs/pia_sweep_%s.md' % T
lock('eve22_sweep')
ids2 = []
try:
    run(['tools/pia_soldout_sweep.py', '--group', str(grp), '--apply'], 'eve22_sweep.txt')
    s = io.open(lg, encoding='utf-8').read() if os.path.exists(lg) else ''
    sec = s.split('## ぴあにあって登録に無い', 1)[1].split('\n## ', 1)[0] if '## ぴあにあって登録に無い' in s else ''
    ids2 = sorted({int(x) for x in re.findall(r'id(\d+)', sec)})
    W('組%d 取りこぼし %d件' % (grp, len(ids2)))
    if ids2:
        a2 = ','.join(map(str, ids2))
        run(['tools/heal_stale_deadlines.py', '--ids', a2, '--build'], 'eve22_sw_build.txt')
        t = run(['tools/heal_stale_deadlines.py', '--apply', '--ids', a2], 'eve22_sw_apply.txt')
        union_if_blocked(t, 'sweep')
        hc = run(['tmp/heal_head_compare_1805.py'], 'eve22_sw_hc.txt')
        W('組 HEAD比べ %s' % (hc.strip().splitlines()[-1] if hc.strip() else '?'))
    run(['tools/compact_events.py', '--apply'], 'eve22_sw_compact.txt')
finally:
    unlock()
if ids2:
    t = run(['tools/reconcile_pia.py', '--ids', ','.join(map(str, ids2))], 'eve22_sw_rec.txt')
    m = re.search(r'集計: (.+?) ===', t)
    W('組 照合し直し %s' % (m.group(1) if m else '?'))
msg('msg_eve22s.txt', '11/22 夕方（遅れた昼の分）（commit だけ）：ぴあの見直し 組%d＝売り切れの印・取りこぼし %d件を heal --ids（止まった分は足し算・HEAD比べ・compact）→ reconcile_pia --ids（%s）' % (grp, len(ids2), lg))
run(['tmp/x1112/commit.py', D + 'msg_eve22s.txt', lg], 'eve22_commit_s.txt')
io.open(D + 'eve22.done', 'w').write('done')
W('おわり')
