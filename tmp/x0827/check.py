# -*- coding: utf-8 -*-
import sys,re,io,glob
sys.stdout.reconfigure(encoding='utf-8')
for p in sorted(glob.glob('tmp/x0827/post*.txt')):
    t=io.open(p,encoding='utf-8').read().rstrip('\n')
    body=t.split('▼チケット情報はこちら')[0].rstrip()
    n=len(re.sub(r'\s','',body))
    # 「。」の直後が改行でない箇所
    bad=[m.start() for m in re.finditer(r'。(?!\n|$)',t)]
    print('%s 本文%d字 | 「。」の後が改行でない %d箇所 | CTA:%s | URL:%s | タグ:%d'%(
        p.split('/')[-1], n, len(bad),
        '▼チケット情報はこちら' in t, 'https://oshinavi.jp' in t, len(re.findall(r'#\S+',t))))
    for b in bad[:3]: print('     →',repr(t[max(0,b-25):b+8]))
