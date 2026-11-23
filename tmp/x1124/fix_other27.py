# -*- coding: utf-8 -*-
# 11/24 札の無い TicketDive 27件：係が名前で検索して出典つきで分かった15件を入れ直す（57731 は出典が弱い＝その他のまま）
import io, json, os, re, time
os.chdir('C:/Users/user/oshinavi')
G = {57722: 'idol', 57723: 'idol', 57725: 'fanevent', 57728: 'fanevent', 57732: 'tiktoker', 57734: 'anime', 57740: 'idol',
     57742: 'fanevent', 57743: 'musicetc', 57744: 'idol', 57745: 'idol', 57747: 'idol', 57749: 'idol', 57750: 'musicetc', 57751: 'rock'}
LK = 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'fix_other27'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    text = io.open('index.html', encoding='utf-8', newline='').read()
    m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
    st = m.start(1)
    E, end = json.JSONDecoder().raw_decode(text, st)
    n = 0
    for e in E:
        if e['id'] in G and e.get('genre') == 'other':
            e['genre'] = G[e['id']]
            e.pop('_otherByRule', None)
            n += 1
    body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E) + '\n]'
    text = text[:st] + body.replace('\n', '\r\n') + text[end:]
    io.open('index.html', 'wb').write(text.encode('utf-8'))
    print('入れ直した', n)
finally:
    os.remove(LK)
