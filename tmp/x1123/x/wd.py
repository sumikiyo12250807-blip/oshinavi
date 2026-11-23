# -*- coding: utf-8 -*-
import datetime, io, subprocess, glob
o = io.open('C:/Users/user/oshinavi/tmp/x1123/x/wd.txt', 'w', encoding='utf-8')
o.write('2027-03-16 %s\n' % '月火水木金土日'[datetime.date(2027, 3, 16).weekday()])
for f in sorted(glob.glob('C:/Users/user/oshinavi/tmp/x1123/x/post/*.txt')):
    r = subprocess.run(['python', 'C:/Users/user/oshinavi/tools/x_check.py', f], capture_output=True, text=True, encoding='utf-8', errors='replace')
    o.write('%s rc=%d %s\n' % (f[-9:], r.returncode, (r.stdout + r.stderr).strip()[-300:]))
