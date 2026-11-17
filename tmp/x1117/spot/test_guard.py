# -*- coding: utf-8 -*-
import json, subprocess, sys
H = 'C:/Users/user/oshinavi/.claude/hooks/pia_sweep_guard.py'
for c in ('git -C C:/Users/user/oshinavi push origin main', 'git status', 'echo "git push を止める"'):
    r = subprocess.run([sys.executable, H], input=json.dumps({'tool_input': {'command': c}}).encode(), capture_output=True)
    print(repr(c), 'rc', r.returncode, r.stderr.decode('utf-8')[:160])
