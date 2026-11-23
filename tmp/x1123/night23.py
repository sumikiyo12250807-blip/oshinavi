# -*- coding: utf-8 -*-
# 11/23 夜の便（commit だけ・push は最後に別で）：1本ずつ順に
#  1) ぴあの見直し 今日の組（noon23 の5番を写した＝昼はメモリ不足で止められて回っていない）
#  2) 全体の隠れ枠ヒール（noon23b＝止まった分は足し算・HEAD比べ・compact・check_order）
#  e+ の3分の1の照合は e+ を叩く＝この鎖のあと別に（ぴあと e+ は重ねてよいが、重い道具は1本ずつ＝メモリ）
import io, os, re, subprocess, sys, time, datetime
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1123/'
T = '2026-11-23'
LK = 'tmp/x1112/index.lock'
log = io.open(D + 'night23.txt', 'a', encoding='utf-8')
def W(m):
    log.write(time.strftime('%H:%M:%S ') + m + '\n'); log.flush()
def run(a, out):
    r = subprocess.run([sys.executable] + a, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    io.open(D + out, 'w', encoding='utf-8').write('rc=%d\n%s\n%s' % (r.returncode, r.stdout, r.stderr))
    W('=== %s rc %d' % (' '.join(a)[:90], r.returncode))
    return r.stdout + '\n' + r.stderr
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

W('開始')
grp = datetime.date(2026, 11, 23).toordinal() % 3
lg = 'logs/pia_sweep_%s.md' % T
W('ぴあの見直し 組%d 始め' % grp)
# 見直しは読むのが長い（2時間ほど）＝鍵は書く時だけ取る：--apply は道具が自分で書く。ここは鍵を取って流す（昼の形のまま）
lock('night23_sweep')
ids2 = []
try:
    run(['tools/pia_soldout_sweep.py', '--group', str(grp), '--apply'], 'night23_sweep.txt')
    s = io.open(lg, encoding='utf-8').read() if os.path.exists(lg) else ''
    sec = s.split('## ぴあにあって登録に無い', 1)[1].split('\n## ', 1)[0] if '## ぴあにあって登録に無い' in s else ''
    ids2 = sorted({int(x) for x in re.findall(r'id(\d+)', sec)})
    W('組%d 取りこぼし %d件' % (grp, len(ids2)))
    if ids2:
        a2 = ','.join(map(str, ids2))
        run(['tools/heal_stale_deadlines.py', '--ids', a2, '--build'], 'night23_sw_build.txt')
        t = run(['tools/heal_stale_deadlines.py', '--apply', '--ids', a2], 'night23_sw_apply.txt')
        if '🛡️' in t:
            blk = t.split('🛡️', 1)[1].split('🚨', 1)[0]
            b = re.findall(r'^\s+id=(\d+)', blk, re.M)
            if b:
                io.open('tmp/heal_blocked_hold_1805.txt', 'w', encoding='utf-8').write(','.join(b))
                run(['tools/heal_union_stale.py', '--ids-src', '--apply'], 'night23_sw_union.txt')
        hc = run(['tmp/heal_head_compare_1805.py'], 'night23_sw_hc.txt')
        W('組 HEAD比べ %s' % (hc.strip().splitlines()[-1] if hc.strip() else '?'))
    run(['tools/compact_events.py', '--apply'], 'night23_sw_compact.txt')
finally:
    unlock()
if ids2:
    t = run(['tools/reconcile_pia.py', '--ids', ','.join(map(str, ids2))], 'night23_sw_rec.txt')
    m = re.search(r'集計: (.+?) ===', t)
    W('組 照合し直し %s' % (m.group(1) if m else '?'))
msg('msg_night23s.txt', '11/23 夜（commit だけ）：ぴあの見直し 組%d＝売り切れの印・取りこぼし %d件を heal --ids（止まった分は足し算・HEAD比べ・compact）→ reconcile_pia --ids（%s）' % (grp, len(ids2), lg))
run(['tmp/x1112/commit.py', D + 'msg_night23s.txt', lg], 'night23_commit_s.txt')
# 2) 全体ヒール
W('全体ヒール 始め')
b = run(['tools/heal_stale_deadlines.py', '--build'], 'night23_build.txt')
m = re.search(r'=== convert .*', b); W(m.group(0) if m else '?')
lock('night23_heal')
try:
    t = run(['tools/heal_stale_deadlines.py', '--apply'], 'night23_apply.txt')
    if '🛡️' in t:
        blk = t.split('🛡️', 1)[1].split('🚨', 1)[0]
        b2 = re.findall(r'^\s+id=(\d+)', blk, re.M)
        if b2:
            io.open('tmp/heal_blocked_hold_1805.txt', 'w', encoding='utf-8').write(','.join(b2))
            run(['tools/heal_union_stale.py', '--ids-src', '--apply'], 'night23_union.txt')
            W('止まった %d件 を足し算' % len(b2))
    hc = run(['tmp/heal_head_compare_1805.py'], 'night23_hc.txt')
    W('HEAD比べ ' + (hc.strip().splitlines()[-1] if hc.strip() else '?'))
    run(['tools/compact_events.py', '--apply'], 'night23_compact.txt')
finally:
    unlock()
r = subprocess.run(['node', 'tools/check_order.js'], capture_output=True, text=True, encoding='utf-8', errors='replace')
io.open(D + 'night23_order.txt', 'w', encoding='utf-8').write(r.stdout + r.stderr)
W('check_order ' + ' '.join((r.stdout + r.stderr).strip().splitlines()[-2:])[:200])
msg('msg_night23h.txt', '11/23 夜（commit だけ）：全体の隠れ枠ヒール --build → --apply（止まった分は足し算）・HEAD比べ・compact・check_order')
run(['tmp/x1112/commit.py', D + 'msg_night23h.txt'], 'night23_commit_h.txt')
io.open(D + 'night23.done', 'w').write('done')
W('おわり')
