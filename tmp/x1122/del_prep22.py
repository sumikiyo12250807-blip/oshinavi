# -*- coding: utf-8 -*-
# 11/22（遅れた朝の分）：期限切れの削除の下見（11/21 の形を日付だけ進めて写す）＝check_expired と独立再導出（削除は誤りという前提）が一致した分だけ
import io, os, subprocess, sys
R = 'C:/Users/user/oshinavi/'
os.chdir(R)
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1122/'
os.makedirs(D + 'agent_del', exist_ok=True)
s = io.open('tmp/x1121/agent_del/scan.py', encoding='utf-8').read()
s = s.replace('TODAY = dt.date(2026, 11, 21)', 'TODAY = dt.date(2026, 11, 22)').replace('CUT = dt.date(2026, 11, 20)', 'CUT = dt.date(2026, 11, 21)').replace('tmp/x1121/', 'tmp/x1122/')
assert 'TODAY = dt.date(2026, 11, 22)' in s and 'CUT = dt.date(2026, 11, 21)' in s
io.open(D + 'agent_del/scan.py', 'w', encoding='utf-8').write(s)
s = io.open('tmp/x1121/parse_expired.py', encoding='utf-8').read().replace('tmp/x1121/', 'tmp/x1122/')
io.open(D + 'parse_expired.py', 'w', encoding='utf-8').write(s)
s = io.open('tmp/x1121/del_apply.py', encoding='utf-8').read().replace('tmp/x1121/', 'tmp/x1122/')
s = s.replace("CUT = '2026-11-20'", "CUT = '2026-11-21'").replace('bak_1121_del', 'bak_1122_del').replace("b'del_apply21'", "b'del_apply22'")
s = s.replace("## 2026-11-21 朝の便で削除したエントリ（期限切れ）", "## 2026-11-22 夕方（遅れた朝の分）で削除したエントリ（期限切れ）")
s = s.replace("logs/removed_2026-11-21.md", "logs/removed_2026-11-22.md")
assert "CUT = '2026-11-21'" in s and 'removed_2026-11-22.md' in s and 'bak_1122_del' in s and 'tmp/x1121' not in s
io.open(D + 'del_apply.py', 'w', encoding='utf-8').write(s)
subprocess.run([sys.executable, D + 'parse_expired.py'], env=env)
a = subprocess.run([sys.executable, D + 'agent_del/scan.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
b = subprocess.run([sys.executable, D + 'del_apply.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
io.open(D + 'del_prep.txt', 'w', encoding='utf-8').write(a.stdout + a.stderr + '\n----\n' + b.stdout + b.stderr)
