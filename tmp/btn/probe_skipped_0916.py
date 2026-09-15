# -*- coding: utf-8 -*-
"""組み立てで「売切」で飛ばされた候補を、ぴあで1件ずつ開いて本当に売り切れか確かめる（読むだけ・2026-09-16 深夜）
混雑ページ（sorry.pia）を掴んで「買える枠0」に見えただけかを見分けるため、1件ごとに8秒空ける。
使い方: python probe_skipped_0916.py <eventCd> [<eventCd> ...]
"""
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
for i, cd in enumerate(sys.argv[1:]):
    if i:
        time.sleep(8)
    r = subprocess.run([sys.executable, 'tools/pia_tickets.py', cd, '--all'], capture_output=True)
    out = (r.stdout or b'').decode('utf-8', 'replace').strip().splitlines()
    err = (r.stderr or b'').decode('utf-8', 'replace').strip().splitlines()
    print('=== %s（終了コード %d・%d行）' % (cd, r.returncode, len(out)))
    for ln in out[:12]:
        print('  ' + ln[:150])
    for ln in err[-3:]:
        print('  [err] ' + ln[:150])
