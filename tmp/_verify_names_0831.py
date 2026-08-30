# e+の生HTMLから「出演」欄と公演名を自分で抜き直す（エージェントの結論を使わない）
import re,sys,json,os,html
sys.stdout.reconfigure(encoding='utf-8')
IDS=[5989,5991,5994,5995,5998,5999,6001,6002,6005,6006,6008,6010,6011,6012,6015,6017,6020,6021,6023]
for i in IDS:
    p=f'tmp/_agentB_cache/{i}.html'
    if not os.path.exists(p): print(i,'キャッシュ無し'); continue
    h=open(p,encoding='utf-8',errors='replace').read()
    # 出演の表記ゆれを全部拾う
    cands=[]
    for pat in (r'"(?:artist|shutsuen|cast)[^"]*"\s*:\s*"([^"]{2,200})"',
                r'出演[^<]{0,6}</[^>]+>\s*<[^>]+>([^<]{2,200})',
                r'出演[：:]\s*([^<\n]{2,200})'):
        for m in re.finditer(pat,h):
            v=html.unescape(m.group(1)).strip()
            if v and v not in cands: cands.append(v)
    title=''
    m=re.search(r'<title>(.*?)</title>',h,re.S)
    if m: title=html.unescape(m.group(1)).strip()[:70]
    print(f'--- id={i}')
    print(f'    title: {title}')
    for c in cands[:4]: print(f'    出演候補: {c[:120]}')
