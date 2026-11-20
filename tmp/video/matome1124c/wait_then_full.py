# -*- coding: utf-8 -*-
# クーザの全編の書き出し（tmp/video/kooza1110/full_running.flag）が終わるのを待つ → お笑いの全編（run_full＝前半・後半2本同時・自分の flag を作って消す）
#   → Downloads/oshinavi_1113_owarai_matome.mp4 に写す → final_1113.py（長さ・音ずれ・字幕の塊と USLT・塊ごとのコマ）・締めの1コマ（105 秒）
import io, os, shutil, subprocess, sys, time, datetime
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
K = 'tmp/video/kooza1110/full_running.flag'
log = io.open(D + 'wait_then_full.txt', 'w', encoding='utf-8')
t0 = time.time()
while os.path.exists(K):
    time.sleep(15)
log.write('クーザの印が消えた（%d 秒待った）%s\n' % (time.time() - t0, datetime.datetime.now().strftime('%H:%M:%S'))); log.flush()
r = subprocess.run([sys.executable, D + 'run_full.py'], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.write('run_full rc %s %s\n%s\n' % (r.returncode, datetime.datetime.now().strftime('%H:%M:%S'), io.open(D + 'run_full.txt', encoding='utf-8').read() if os.path.exists(D + 'run_full.txt') else '')); log.flush()
V = D + 'out_x.mp4'
if r.returncode == 0 and os.path.exists(V):
    shutil.copyfile(V, 'C:/Users/user/Downloads/oshinavi_1113_owarai_matome.mp4')
    log.write('Downloads に写した %.2fMB\n' % (os.path.getsize(V) / 1048576)); log.flush()
    r2 = subprocess.run([sys.executable, D + 'final_1113.py'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    log.write('final rc %s %s\n' % (r2.returncode, r2.stderr[-800:]))
    import imageio_ffmpeg
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-v', 'error', '-ss', '105.0', '-i', V, '-frames:v', '1', D + 'final/end_105.png'])
log.close()
open(D + 'wait_then_full.done', 'w').close()
