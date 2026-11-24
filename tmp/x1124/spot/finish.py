# -*- coding: utf-8 -*-
# 57106 の名前の崩れ（会場名の括弧の中の括弧）を直す（鍵の中）→ 番人 → commit
import io, os, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
sys.path.insert(0, 'tools')
import compact_events as C
env = dict(os.environ, PYTHONIOENCODING='utf-8')
LK = 'tmp/x1112/index.lock'
D = 'tmp/x1124/spot/'
out = io.open(D + 'finish.txt', 'w', encoding='utf-8')
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'spot_finish24'); os.close(fd); break
    except FileExistsError:
        time.sleep(15)
try:
    t = io.open('index.html', encoding='utf-8', newline='').read()
    E = C.load(t)
    e = {x['id']: x for x in E}[57106]
    assert e['name'].startswith('さいたまブロンコス ）')
    e['name'] = 'さいたまブロンコス 【ハーフシーズンシート】所沢開催8試合プラン'
    s, end, _ = C.locate(t)
    t = t[:s] + C.dump(E, True, '\r\n') + t[end:]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(t)
finally:
    os.remove(LK)
def run(a):
    r = subprocess.run(a, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('=== %s rc=%d\n%s\n%s\n' % (' '.join(a), r.returncode, r.stdout[-2500:], r.stderr[-800:])); out.flush()
    return r
run(['node', 'tools/gate_badge_render.js'])
run([sys.executable, 'tools/gate_fields.py'])
io.open(D + 'msg.txt', 'w', encoding='utf-8').write(
    '11/24 13:07 抜き打ち30件（commit だけ）：🔴2🟠5🟡1 を直した＝57757 B.LEAGUE ハーフシーズンシート（売り場「1/19に試合はございません」なのに試合の日に見えていた）＋同じ型の5件・build_bleague_entries をシーズンシート/席パックはセット販売として組む形に／33595 CONTI-NeW FeS 三次先行(10/21終了)→★一般発売・出演者の崩れ／5158 GOODWARP・48625 吉田山田 ぴあの2次・3次プレリザーブを足し算で取り直し／48862・7140 出演者／4194 ダンスの札／4507 終わった神奈川の2枠\n\n'
    'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n')
r = run([sys.executable, 'tmp/x1112/commit.py', D + 'msg.txt', 'index.html', 'tools/build_bleague_entries.py', 'tmp/x1124/spot'])
out.close()
print('ok')
