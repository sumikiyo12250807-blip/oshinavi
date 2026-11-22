# -*- coding: utf-8 -*-
# 11/22 X の独立FCで見つけた登録の崩れを直す（鍵）
#   54916 神田伯山＝出演者の欄に e+ の「前座は14:15から上がります」の切れ端（「15から上がります／45から上がります」）→ 神田伯山 だけに
#   37656 南佳孝＝出演者の欄と公演名が入れ替わっている → 入れ替える
#   bg_used.md に 11/26 演歌と舞台の背景 37497 の行
import io, os, sys, time, json
os.chdir('C:/Users/user/oshinavi')
sys.path.insert(0, 'tools')
import compact_events as C
LK = 'tmp/x1112/index.lock'
log = io.open('tmp/x1122/fix_reg22.txt', 'w', encoding='utf-8')
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'fix_reg22'); os.close(fd); break
    except FileExistsError:
        time.sleep(15)
try:
    s = io.open('index.html', encoding='utf-8', newline='').read()
    a, b, E = C.locate(s)
    for e in E:
        if e.get('id') == 54916:
            log.write('54916 前 %r\n' % e.get('artist'))
            if '上がります' in (e.get('artist') or ''):
                e['artist'] = '神田伯山'
            log.write('54916 後 %r\n' % e.get('artist'))
        if e.get('id') == 37656:
            log.write('37656 前 name=%r artist=%r\n' % (e.get('name'), e.get('artist')))
            if e.get('name') == '南佳孝' and e.get('artist') and e.get('artist') != '南佳孝':
                e['name'], e['artist'] = e['artist'], e['name']
            log.write('37656 後 name=%r artist=%r\n' % (e.get('name'), e.get('artist')))
    nl = '\r\n' if '\r\n' in s[:5000] else '\n'
    s2 = s[:a] + C.dump(E, C.is_compact(s), nl) + s[b:]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(s2)
    log.write('カード %d\n' % len(C.locate(io.open('index.html', encoding='utf-8', newline='').read())[2]))
finally:
    os.remove(LK)
p = 'tmp/video/bg_used.md'
t = io.open(p, encoding='utf-8').read()
if '37497' not in t:
    io.open(p, 'a', encoding='utf-8').write('\n- 2026-11-22 37497（青空と緑の丘）＝11/26 演歌と舞台まとめ（ミュージカル調の姐さん）\n')
log.close()
