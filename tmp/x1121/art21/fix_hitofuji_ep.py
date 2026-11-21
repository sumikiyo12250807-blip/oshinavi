# -*- coding: utf-8 -*-
# 54098 一富士茄子牛焦げルギー e+：9回とも 11/22 10:00〜 一般発売の窓が登録に無い（reconcile_eplus m-未登録窓）
#  ＝同じ URL の2次プレオーダーの枠と同じ形で、締切を実頁どおりに足す（鍵の中）→ reconcile_eplus --ids 54098
import io, os, sys, time, json, subprocess
os.chdir('C:/Users/user/oshinavi')
sys.path.insert(0, 'tools')
import compact_events as C
END = {
    'P0030012P021005': '2027-01-05', 'P0030012P021001': '2027-01-06', 'P0030012P021003': '2027-01-06',
    'P0030012P021002': '2027-01-07', 'P0030012P021004': '2027-01-07', 'P0030013P021009': '2027-01-11',
    'P0030013P021007': '2027-01-12', 'P0030013P021006': '2027-01-13', 'P0030013P021008': '2027-01-13',
}
PFX = 'https://eplus.jp/sf/detail/3368360001-'
LK = 'tmp/x1112/index.lock'
out = io.open('tmp/x1121/art21/fix_hitofuji_ep.txt', 'w', encoding='utf-8')
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'fix_hitofuji_ep'); os.close(fd); break
    except FileExistsError:
        time.sleep(15)
try:
    t = io.open('index.html', encoding='utf-8', newline='').read()
    E = C.load(t)
    e = [x for x in E if x['id'] == 54098][0]
    add = []
    for k, d in END.items():
        u = PFX + k
        old = [x for x in e['tickets'] if x.get('url') == u]
        assert len(old) == 1, (k, len(old))
        assert '2次プレオーダー' in old[0]['type']
        m = old[0]['type'].split('（', 1)[1].split('）', 1)[0]
        nt = dict(old[0])
        for f in ('soldOut', 'saleUntilSoldOut', 'status'):
            nt.pop(f, None)
        nt['type'] = '一般発売（%s）11/22 10:00発売' % m
        nt['date'] = d
        nt['startDate'] = '2026-11-22'
        add.append(nt)
        out.write('足した枠 %s\n' % json.dumps(nt, ensure_ascii=False))
    e['tickets'].extend(add)
    s, end, _ = C.locate(t)
    t = t[:s] + C.dump(E, True, '\r\n') + t[end:]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(t)
finally:
    os.remove(LK)
r = subprocess.run([sys.executable, 'tools/reconcile_eplus.py', '--ids', '54098'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=dict(os.environ, PYTHONIOENCODING='utf-8'))
out.write('=== reconcile_eplus --ids 54098 rc=%d\n%s\n%s\n' % (r.returncode, r.stdout[-3000:], r.stderr[-600:]))
