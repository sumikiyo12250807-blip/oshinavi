# -*- coding: utf-8 -*-
"""「最新CD」ボタンが無い音楽エントリ（単独名義）に、Amazonで実測してCDが出るものだけ links.amazon を付ける（2026-09-26 夜・ユーザー「全部付けて」「洋楽ももちろん」）。
  python tmp/x0926/amazon_fill.py          # 実測（途中から再開できる・tmp/x0926/amazon_fill.json に貯める）
  python tmp/x0926/amazon_fill.py --apply  # ヒットした分だけ index.html に書く
"""
import io, json, re, sys, os, time
sys.path.insert(0, 'tools')
import amazon_audit as A
from check_expired import extract_events_array
MG = {'jpop','rock','idol','kpop','hiphop','classic','anime','seiyuu','vtuber','youtuber','enka','jazz','yougaku'}
OUT = 'tmp/x0926/amazon_fill.json'
def kw_of(name):
    kw = re.sub(r'＜.*?＞', '', name); kw = re.sub(r'（.*?）', '', kw)
    kw = re.split(r'\s+(?:トーク|コンサート|ツアー|ＬＩＶＥ|LIVE|Ｌｉｖｅ|ライブ|リサイタル|ギター|シネマ|２０[０-９]{2}|20\d\d|ｉｎ|周年)', kw)[0].strip('　 ').strip()
    import unicodedata
    return unicodedata.normalize('NFKC', kw)
E = extract_events_array('index.html')
miss = [e for e in E if e.get('genre') in MG and not (e.get('links') or {}).get('amazon') and not re.search(r'[／×/]|、| & ', e.get('artist',''))]
arts = {}
for e in miss:
    k = kw_of(e.get('artist',''))
    if k: arts.setdefault(k, {'classic': e.get('genre')=='classic', 'ids': []})['ids'].append(e['id'])
res = json.load(io.open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {}
if '--apply' in sys.argv:
    p='index.html'; t=io.open(p,encoding='utf-8',newline='').read()
    m=re.search(r'const\s+EVENTS\s*=\s*(\[)',t); s=m.start(1); ev,e=json.JSONDecoder().raw_decode(t,s)
    idmap={}
    for k,r in res.items():
        if r.get('hit'):
            for i in r['ids']: idmap[i]=A.amazon_url(k, r['with_cd'])
    n=0
    for x in ev:
        if x['id'] in idmap and not (x.get('links') or {}).get('amazon'):
            x.setdefault('links',{})['amazon']=idmap[x['id']]; n+=1
    body=json.dumps(ev,ensure_ascii=False,indent=2).replace('\r\n','\n').replace('\n','\r\n')
    d=(t[:s]+body+t[e:]).encode('utf-8'); assert d.count(b'\r\n')==d.count(b'\n'); io.open(p,'wb').write(d)
    print('applied', n); sys.exit()
todo = [k for k in arts if k not in res]
print('artists', len(arts), 'done', len(res), 'todo', len(todo), flush=True)
zero_run = 0
for i, k in enumerate(todo, 1):
    wc = not arts[k]['classic']
    n, err = A.probe2(k, wc)
    if (n is None or n < A.HIT_MIN) and wc is True:
        n2, err2 = A.probe2(k, False)   # 名前だけでも試す
        if n2 is not None and (n is None or n2 > n): n, wc = n2, False
    hit = n is not None and n >= A.HIT_MIN
    res[k] = {'ids': arts[k]['ids'], 'n': n, 'with_cd': wc, 'hit': hit, 'err': err}
    zero_run = 0 if (n or 0) > 0 else zero_run + 1
    if i % 10 == 0 or zero_run >= 12:
        io.open(OUT, 'w', encoding='utf-8').write(json.dumps(res, ensure_ascii=False, indent=0))
        print('[%d/%d] hits=%d' % (i, len(todo), sum(1 for r in res.values() if r['hit'])), flush=True)
    if zero_run >= 12:
        print('STOP: 0件が12回続いた（Amazonの絞り込み疑い）。時間を置いて再開する', flush=True); break
io.open(OUT, 'w', encoding='utf-8').write(json.dumps(res, ensure_ascii=False, indent=0))
print('done hits=%d / %d' % (sum(1 for r in res.values() if r['hit']), len(res)), flush=True)
