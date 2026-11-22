# -*- coding: utf-8 -*-
# 昨日の機械の突き合わせ fc_check_1122.py を 11/23 発売用に日付を1日進めて写す
import io
R = 'C:/Users/user/oshinavi/tmp/'
s = io.open(R + 'x1121/x/fc_check_1122.py', encoding='utf-8').read()
s = s.replace('x1121', 'x1122')
for a, b in [('11-24', '11-25'), ('11/24', '11/25'), ('11-23', '11-24'), ('11/23', '11/24'), ('11-22', '11-23'), ('11/22', '11/23'), ('fc_check_1122', 'fc_check_1123')]:
    s = s.replace(a, b)
io.open(R + 'x1122/x/fc_check_1123.py', 'w', encoding='utf-8').write(s)
print([l for l in s.splitlines() if '112' in l][:12])
