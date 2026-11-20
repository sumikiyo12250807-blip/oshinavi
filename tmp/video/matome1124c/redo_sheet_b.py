# -*- coding: utf-8 -*-
# 11/17 すちこ「姐さんの画像が雑よね　髪形がいつも同じ」→「キャラクター着席編集」のチャットで描き直した 9人（sheet_b.png）に差し替え
#   → 切り抜き（port_1120 の切り抜き部分）→ set_1120（s/t を作り直し・設定）→ 絵コンテの静止画・試し動画（board_1120）→ ページ
import io, os, shutil, subprocess, sys
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
V = 'C:/Users/user/oshinavi/tmp/video/'
log = io.open(D + 'redo_sheet_b.txt', 'w', encoding='utf-8')
def run(a, cwd=None):
    r = subprocess.run([sys.executable] + a, capture_output=True, text=True, encoding='utf-8', errors='replace', cwd=cwd)
    log.write('== %s rc=%d\n%s\n' % (' '.join(a)[-70:], r.returncode, (r.stdout + r.stderr)[-1500:])); log.flush()
    return r.returncode
shutil.copyfile(D + 'sheet.png', D + 'sheet_a_old.png')
shutil.copyfile(D + 'sheet_b.png', D + 'sheet.png')
for f in os.listdir(D + 'poses'):
    os.remove(D + 'poses/' + f)
run([V + 'shuyaku1117/cut17.py', 'sheet.png', 'w', V + 'matome1124c/'], cwd=V + 'matome1124c/')
if os.path.exists(D + 'cut17_w.txt'):
    log.write(io.open(D + 'cut17_w.txt', encoding='utf-8').read())
from PIL import Image
tiles = [Image.open(D + 'poses/w%d.png' % k).convert('RGBA') for k in range(1, 10) if os.path.exists(D + 'poses/w%d.png' % k)]
log.write('切り抜けた %d 人\n' % len(tiles)); log.flush()
th = 360
row = Image.new('RGBA', (sum(int(t.width * th / t.height) + 20 for t in tiles) + 20, th + 40), (0, 150, 60, 255))
x = 20
for t in tiles:
    t2 = t.resize((int(t.width * th / t.height), th), Image.LANCZOS)
    row.alpha_composite(t2, (x, 20)); x += t2.width + 20
row.convert('RGB').save(D + 'contact_cut.png')
if len(tiles) == 9:
    run([D + 'set_1120.py'])
    run([D + 'board_1120.py'])
    run([D + 'mk_page_1120.py'])
open(D + 'redo_sheet_b.done', 'w').close()
