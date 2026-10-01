# -*- coding: utf-8 -*-
# 7.5：ぴあ発売前一覧（10/2〜10/4発売）を全ジャンル順番に読み、OSHINAVIと突き合わせる（ぴあは1本ずつ＝同時に回さない）
import subprocess, io
root = 'C:/Users/user/oshinavi/'
log = io.open(root + 'tmp/x1001/x/pia_days_all.log', 'w', encoding='utf-8')
for lg in ('01', '02', '07', '06', '03', '04', '05'):
    p = subprocess.run(['python', 'tmp/x1001/x/pia_days_list.py', lg], cwd=root, capture_output=True)
    log.write('### lg=%s exit %d\n%s\n' % (lg, p.returncode, (p.stdout + p.stderr).decode('utf-8', 'replace')[:3000]))
    log.flush()
    p = subprocess.run(['python', 'tmp/x1001/x/true_missing.py', 'tmp/x1001/x/pia_days_%s.txt' % lg], cwd=root, capture_output=True)
    log.write('--- true_missing\n%s\n' % (p.stdout + p.stderr).decode('utf-8', 'replace')[:3000])
    log.flush()
