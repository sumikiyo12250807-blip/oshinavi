# -*- coding: utf-8 -*-
# 11/21 ロック（70年代ソウルの姐さん）：タップ画面を撮る → 絵コンテの静止画（0秒のカバー・場面ごと・締め）→ 試し動画2本（頭 0〜30 秒／締め 54〜88 秒）
#   試し動画は、もう1人の係（shuyaku1119）の書き出しが走っている間は待つ＝重い道具は同時2本まで
import io, os, glob, shutil, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
log = []
def W():
    io.open(D + 'board_1121.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
def busy():
    r = subprocess.run(['powershell', '-NoProfile', '-Command',
                        "(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -like '*shuyaku1119*' -and ($_.CommandLine -like '*render*' -or $_.CommandLine -like '*clip*' -or $_.CommandLine -like '*par*') }).Count"],
                       capture_output=True, text=True, errors='replace')
    try:
        return int((r.stdout or '0').strip() or 0)
    except ValueError:
        return 0
r = subprocess.run([sys.executable, D + 'shoot_badge.py'], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.append('badge rc=%d %s' % (r.returncode, (r.stdout + r.stderr)[-600:])); W()
for f in glob.glob(D + 'frames/h_*.png'):
    os.remove(f)
T = [0.0, 3.5, 7.5, 12.5, 17.0, 21.0, 24.5, 28.5, 31.5, 36.0, 40.0, 42.5, 45.5, 49.0, 53.0, 58.0, 62.0, 66.0, 72.0, 80.0, 87.0]
r = subprocess.run([sys.executable, D + 'render.py', '--frames', ','.join(str(t) for t in T)], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.append('frames rc=%d %s' % (r.returncode, (r.stdout + r.stderr)[-1500:])); W()
for nm, a, b in (('clip_a', 0.0, 30.0), ('clip_b', 54.0, 88.44)):
    t0 = time.time()
    while busy() and time.time() - t0 < 2400:
        time.sleep(20)
    log.append('%s 待った %.0f 秒' % (nm, time.time() - t0)); W()
    t0 = time.time()
    r = subprocess.run([sys.executable, D + 'render.py', '--clip', '%s,%s' % (a, b)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if os.path.exists(D + 'clip.mp4'):
        shutil.copyfile(D + 'clip.mp4', D + nm + '.mp4')
    log.append('%s %.1f〜%.1f 秒 rc=%d %.0f 秒かかった %s' % (nm, a, b, r.returncode, time.time() - t0, (r.stdout + r.stderr).strip()[-300:])); W()
io.open(D + 'board_1121.done', 'w').write('done')
