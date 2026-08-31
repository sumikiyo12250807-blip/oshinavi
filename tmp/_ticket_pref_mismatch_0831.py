# 枠の文言に書かれた県が、エントリの県にも会場にも出てこないものを探す
#（別公演の枠が紛れ込んだサイン＝桂文珍4670で実際に見つかった型）
import json,re,sys
sys.stdout.reconfigure(encoding='utf-8')
s=open('index.html',encoding='utf-8').read()
ev=json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n',s,re.S).group(1))
PREF=re.findall(r'"([^"]+)":\s*"(?:hokkaido|tohoku|kanto|chubu|kinki|chugoku|shikoku|kyushu|kaigai)"',
                re.search(r'PREFECTURE_TO_REGION\s*=\s*\{(.*?)\n\s*\};',s,re.S).group(1))
bad=[]
for e in ev:
    own=(e.get('prefecture','') or '')+' '+(e.get('venue','') or '')+' '+(e.get('dateLabel','') or '')
    if '全国' in (e.get('prefecture') or ''): continue
    for t in e.get('tickets',[]):
        m=re.search(r'[（(]([^）)]*?)\s+(?:R9年\s*)?\d{1,2}/\d',t.get('type',''))
        if not m: continue
        for p in re.split(r'[・/／]',m.group(1)):
            p=p.strip()
            if p and p in PREF and p not in own:
                bad.append((e['id'],e.get('artist','')[:26],e.get('prefecture'),p,t.get('type','')[:44]))
print('枠の県がエントリに無い＝混入の疑い',len(bad),'件')
seen=set()
for b in bad:
    if b[0] in seen: continue
    seen.add(b[0]); print(f"  id{b[0]:5} {b[1]:28} エントリ県[{b[2]}] ← 枠に[{b[3]}] {b[4]}")
print('エントリ数',len(seen))
