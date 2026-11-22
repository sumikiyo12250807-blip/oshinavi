# -*- coding: utf-8 -*-
# 11/22 遅れた朝の push（今日1回目）：夜中の3本（出演者の欄の取り直し M 2,491件・ヒールの道具の直し・11/26 の歌詞）を公開
#   → prepush（x1121 の形）→ 止める行0なら commit → push → 公開の最終更新
import io, os, re, subprocess, sys, time, urllib.request
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1121/'
O = 'tmp/x1122/'
log = io.open(O + 'push_am22.txt', 'w', encoding='utf-8')
def w(t):
    log.write(time.strftime('%H:%M:%S ') + t + '\n'); log.flush()
r = subprocess.run([sys.executable, D + 'prepush.py', '--no-rec'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
t = io.open(D + 'prepush.txt', encoding='utf-8').read()
w(t[-3000:])
bad = [l for l in t.splitlines() if l.startswith('===') and re.search(r'(fold_parts.py --check|gate_badge_render).* rc [^0]', l)] + [l for l in t.splitlines() if '🚨O ' in l]
w('止める行: %r' % bad)
if bad:
    io.open(O + 'push_am22.done', 'w').write('blocked')
    sys.exit()
msg = ('11/22 朝の便（遅れ・今日1回目）：夜中の出演者の欄の取り直し（M 2,491→430）・ヒールの道具の直し・11/26 の歌詞と plan.md を公開 → prepush（畳み・会期・県・会場・欄・画面・並び・枠0・AI/artist ページ＝最終更新・compact）\n\n'
       'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n')
io.open(O + 'msg_push_am22.txt', 'w', encoding='utf-8').write(msg)
c = subprocess.run([sys.executable, 'tmp/x1112/commit.py', O + 'msg_push_am22.txt', 'plan.md'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
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
io.open(O + 'push_am22.done', 'w').write('pushed' if p.returncode == 0 else 'push_failed')
