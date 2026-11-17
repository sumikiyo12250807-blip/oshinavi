# -*- coding: utf-8 -*-
# 11/17 抜き打ち30件（組A ぴあ15＝19/19枠・組B ぴあ以外15＝29/29枠）のズレを売り場どおりに直す（鍵）→ commit だけ
#   ぴあを開かずに直せる分。28413 の出場者は、ぴあの見直しが終わってから refetch_artist --ids で取り直す
import io, os, sys, time, subprocess
R = 'C:/Users/user/oshinavi/'
sys.path.insert(0, R + 'tools')
import compact_events as C
out = []
def fix(e):
    i = e['id']
    T = e['tickets']
    if i == 46001 and not any('当日引換券' in (t.get('type') or '') for t in T):
        T.append({'type': 'ポスター付き当日引換券発売（東京 11/14〜11/29公演）〜11/29 10:00', 'date': '2026-11-29',
                  'url': 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2671040'})
        out.append('46001 ポスター付き当日引換券（東京サンシャイン劇場・〜11/29 10:00・受付中）を足す')
    if i == 55335 and 'Go Go Marchans' not in (e.get('artist') or ''):
        e['artist'] = e['artist'] + '／Go Go Marchans'; out.append('55335 出演者 +Go Go Marchans（オープニングアクト）')
    if i == 41863:
        e['name'] = '伐折羅・参佰弐拾参～煌～'; out.append('41863 公演名 ぴあどおり')
    if i == 50157:
        e['artist'] = '／'.join(io.open(R + 'tmp/x1117/spot/tiget50157_names.txt', encoding='utf-8').read().split('\n'))
        out.append('50157 出演者 TIGET の本文どおり15組')
IDS = (46001, 55335, 41863, 50157)
LK = R + 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'fix_spot1117'); os.close(fd); break
    except FileExistsError:
        time.sleep(15)
try:
    text = io.open(R + 'index.html', encoding='utf-8', newline='').read()
    E = C.load(text)
    for e in E:
        if e['id'] in IDS:
            fix(e)
    s, end, _ = C.locate(text)
    io.open(R + 'index.html', 'w', encoding='utf-8', newline='').write(text[:s] + C.dump(E, True, '\r\n') + text[end:])
finally:
    os.remove(LK)
io.open(R + 'tmp/x1117/spot/fix_spot.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
io.open(R + 'tmp/x1117/spot/msg_spot.txt', 'w', encoding='utf-8').write(
    '11/17（commit だけ）：抜き打ち30件（ぴあ15＝19/19枠・ぴあ以外15＝29/29枠）＝🔴1 46001 梅棒 ポスター付き当日引換券の抜けを足す／🟠 55335 オープニングアクト・41903 e+ 出演（refetch_artist）・50157 TIGET 出演15組／🟡 41863 公演名\n'
    '根っこ：①ぴあの見直し（pia_soldout_sweep）が 11/11 から止まっていた＝push の番人 .claude/hooks/pia_sweep_guard.py を足した ②pia_cast が［オープニングアクト］［出場］を読まなかった＝_CAST_ROLE に足した\n\n'
    'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n')
print('\n'.join(out))
r = subprocess.run([sys.executable, R + 'tmp/x1112/commit.py', R + 'tmp/x1117/spot/msg_spot.txt', 'tools/build_pia_entries.py', '.claude/hooks/pia_sweep_guard.py', 'tools/artist_nocast.json', 'tmp/x1117/spot'], cwd=R, capture_output=True, text=True, encoding='utf-8', errors='replace')
print('commit rc', r.returncode, r.stdout[-300:], r.stderr[-300:])
