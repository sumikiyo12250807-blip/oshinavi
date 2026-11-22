# -*- coding: utf-8 -*-
# 11/22 夕方：抜けた朝・昼の分を 11/21 の道具から写して1本の鎖にする
#   morning_local22（期限切れ・バッジ0・楽天・e+ 今日発売の下見・いつまで不明）→ eve22（e+ 今日発売 --apply・reconcile_eplus --third → fix・ぴあの見直し 今日の組 → heal）→ assign22n（新着の振り分け）
import io
R = 'C:/Users/user/oshinavi/tmp/'
def cp(src, dst, reps):
    s = io.open(R + src, encoding='utf-8').read()
    for a, b in reps:
        assert a in s, (src, a)
        s = s.replace(a, b)
    io.open(R + dst, 'w', encoding='utf-8').write(s)
cp('x1121/morning_local.py', 'x1122/morning_local22.py', [("D = 'tmp/x1121/'", "D = 'tmp/x1122/'"), ("day = '2026-11-21'", "day = '2026-11-22'")])
s = io.open(R + 'x1121/noon21.py', encoding='utf-8').read()
s = s.replace("D = 'tmp/x1121/'", "D = 'tmp/x1122/'").replace("T = '2026-11-21'", "T = '2026-11-22'").replace('datetime.date(2026, 11, 21)', 'datetime.date(2026, 11, 22)')
s = s.replace('noon21', 'eve22').replace('11/21 昼', '11/22 夕方（遅れた昼の分）')
# 2) 今日発売のぴあ・3) TIGET は今日の昼の便（noon22.py の全体ヒール）で済み＝飛ばす
a = s.index('# 2) ぴあ 今日発売'); b = s.index('# 4) e+ 3分の1の照合')
s = s[:a] + "pia, tg = [], []\nmsg('msg_eve22.txt', '11/22 夕方（commit だけ）：e+ heal_eplus_started --apply（遅れた昼の分）')\nrun(['tmp/x1112/commit.py', D + 'msg_eve22.txt'], 'eve22_commit.txt')\n\n" + s[b:]
assert 'x1121' not in s and '2026-11-21' not in s
io.open(R + 'x1122/eve22.py', 'w', encoding='utf-8').write(s)
s = io.open(R + 'x1121/assign21n.py', encoding='utf-8').read()
for a, b in (("'2026-11-21 すちこ「分からないものはその他に」", "'2026-11-21 すちこ「分からないものはその他に」"),
             ("D = 'tmp/x1121/nassign21n/'", "D = 'tmp/x1122/nassign22n/'"), ("b'assign21n_other'", "b'assign22n_other'"), ("b'assign21n'", "b'assign22n'"),
             ("logs/assigned_2026-11-21.md", "logs/assigned_2026-11-22.md"), ("# 2026-11-21 振り分けたエントリ", "# 2026-11-22 振り分けたエントリ"),
             ("## 11/21 昼 新着の振り分け", "## 11/22 夕方 新着の振り分け"), ("'11/21 昼（commit だけ）：新着の振り分け", "'11/22 夕方（commit だけ）：新着の振り分け")):
    assert a in s, a
    s = s.replace(a, b)
io.open(R + 'x1122/assign22n.py', 'w', encoding='utf-8').write(s)
io.open(R + 'x1122/eve22_chain.py', 'w', encoding='utf-8').write('''# -*- coding: utf-8 -*-
# 11/22 夕方の鎖＝1本ずつ順に：morning_local22 → eve22 → assign22n
import io, os, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1122/'
log = io.open(D + 'eve22_chain.txt', 'a', encoding='utf-8')
for f in ('morning_local22.py', 'eve22.py', 'assign22n.py'):
    log.write(time.strftime('%H:%M:%S ') + f + ' 開始\\n'); log.flush()
    r = subprocess.run([sys.executable, D + f], env=env)
    log.write(time.strftime('%H:%M:%S ') + f + ' rc=%d\\n' % r.returncode); log.flush()
open(D + 'eve22_chain.done', 'w').write('done')
''')
print('ok')
