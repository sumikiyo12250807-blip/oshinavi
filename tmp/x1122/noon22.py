# -*- coding: utf-8 -*-
# 11/22 遅れた昼の便（commit だけ）：heal --apply 92件のあと check_order → 止まった41件は足し算（heal_union_stale）→ HEAD比べは夜の prepush → commit
import io, os, subprocess, sys
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open('tmp/x1122/noon22.txt', 'w', encoding='utf-8')
def run(a, tail=1500):
    r = subprocess.run(a, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s rc %s\n%s\n%s\n' % (' '.join(a)[-80:], r.returncode, r.stdout[-tail:], r.stderr[-600:])); out.flush()
    return r.returncode
run([sys.executable, 'tools/heal_union_stale.py', '--apply'], tail=2500)
run(['node', 'tools/check_order.js'])
msg = ('11/22 遅れた昼の便（commit だけ）：隠れ枠ヒール 92件・発売日引き継ぎ 91枠・売り切れの印で残した 62枠／止まった 41件は足し算（heal_union_stale）→ check_order\n\n'
       'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n')
io.open('tmp/x1122/msg_noon22.txt', 'w', encoding='utf-8').write(msg)
run([sys.executable, 'tmp/x1112/commit.py', 'tmp/x1122/msg_noon22.txt', 'plan.md'])
out.close()
