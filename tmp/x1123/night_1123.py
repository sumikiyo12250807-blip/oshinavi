# -*- coding: utf-8 -*-
# 11/22 夜の便（新着の振り分け＝分からない分は その他・宝塚／アイスショーのジャンル／FANY の番人の穴／期限切れ 271件の削除／抜き打ち30件の直し＝出演者の欄と番人2つ／記事で見つけた登録の穴＝一富士 e+・ぴあ／昼の便の直し＝今日発売の締切・e+ 照合・ぴあの見直し 組0・全体の隠れ枠ヒール／県が空のカード 260件／昼に止まった e+ も公開）：今日発売のぴあ heal --ids（鍵）→ 止まった分は足し算 → HEAD比べ → prepush（鍵は prepush が取る）→
# 止める行0なら commit → push（今日の夜の1回）→ 公開の最終更新を確かめる → night_1121.done
import io, os, re, subprocess, sys, time, urllib.request
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1123/'
LK = 'tmp/x1112/index.lock'
log = io.open(D + 'night_1123.txt', 'w', encoding='utf-8')
def w(t):
    log.write(time.strftime('%H:%M:%S ') + t + '\n'); log.flush()
def run(a, out):
    r = subprocess.run([sys.executable] + a, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    t = r.stdout + '\n' + r.stderr
    io.open(D + out, 'w', encoding='utf-8').write('rc=%d\n%s' % (r.returncode, t))
    w('=== %s rc %d\n%s' % (' '.join(a)[:80], r.returncode, '\n'.join(l for l in t.splitlines() if l.startswith('===') or '枠が消えた' in l or 'FIX' in l)[:1500]))
    return t
def lock(tag):
    while True:
        try:
            fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, tag.encode()); os.close(fd); return
        except FileExistsError:
            time.sleep(15)
run(['tmp/x0930/today_pia_ids.py', '2026-11-23'], 'night23p_ids.txt')
ids = io.open('tmp/x0930/today_pia_ids.txt', encoding='utf-8').read().strip()
w('ids ' + ids)
if ids:
    run(['tools/heal_stale_deadlines.py', '--ids', ids, '--build'], 'night23p_build.txt')
    lock('night')
    try:
        t = run(['tools/heal_stale_deadlines.py', '--apply', '--ids', ids], 'night23p_apply.txt')
        if '🛡️' in t:
            blk = t.split('🛡️', 1)[1].split('🚨', 1)[0]
            b = re.findall(r'^\s+id=(\d+)', blk, re.M)
            if b:
                io.open('tmp/heal_blocked_hold_1805.txt', 'w', encoding='utf-8').write(','.join(b))
                w('止まった %d：%s' % (len(b), b))
                run(['tools/heal_union_stale.py', '--ids-src', '--apply'], 'night23p_union.txt')
        run(['tmp/heal_head_compare_1805.py'], 'night23p_hc.txt')
    finally:
        os.remove(LK)
r = subprocess.run([sys.executable, 'tmp/x1121/prepush.py', '--no-rec'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
t = io.open('tmp/x1121/prepush.txt', encoding='utf-8').read()
w(t[-3000:])
bad = [l for l in t.splitlines() if l.startswith('===') and re.search(r'(fold_parts.py --check|gate_badge_render).* rc [^0]', l)] + [l for l in t.splitlines() if '🚨O ' in l]  # gate_fields は H などの件数だけでも rc 1＝O の行だけで止める
w('止める行: %r' % bad)
if bad:
    io.open(D + 'night_1123.done', 'w').write('blocked')
    sys.exit()
msg = ('11/23 夜の便（今日2回目）＝抜き打ち30件の直し・TIGET 全件の作り直し・昼のヒール・ぴあの見直し 今日の組・夜の隠れ枠ヒール／🆕宿のボタンを売り場のバッジのすぐ下に横長で（押すと沈む）・最新CD を Amazon の商品ページへ 19枚・ボタンを数える仕掛けの直し：今日発売のぴあ heal --ids・止まった分は足し算・HEAD比べ／prepush（畳み・会期・県・会場・欄・画面・並び・枠0・AI/artist ページ＝最終更新・compact）\n\n'
       'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n')
io.open(D + 'msg_night23p.txt', 'w', encoding='utf-8').write(msg)
c = subprocess.run([sys.executable, 'tmp/x1112/commit.py', D + 'msg_night23p.txt', 'plan.md'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
w('commit rc=%d %s %s' % (c.returncode, c.stdout[-300:], c.stderr[-300:]))
stamp = re.search(r'id="lastUpdated">([^<]*)<', io.open('index.html', encoding='utf-8').read()).group(1)
w('手元の最終更新 ' + stamp)
p = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True, encoding='utf-8', errors='replace')
w('push rc=%d %s %s' % (p.returncode, p.stdout[-300:], p.stderr[-400:]))
if p.returncode == 0:
    time.sleep(150)
    for k in range(8):
        try:
            h = urllib.request.urlopen(urllib.request.Request('https://oshinavi.jp/?n=%d' % time.time(), headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read().decode('utf-8', 'replace')
            m = re.search(r'id="lastUpdated">([^<]*)<', h)
            got = m.group(1) if m else '見つからない'
            w('公開の最終更新 ' + got)
            if got == stamp:
                break
        except Exception as e:
            w('ERR %s' % e)
        time.sleep(60)
io.open(D + 'night_1123.done', 'w').write('pushed' if p.returncode == 0 else 'push_failed')
