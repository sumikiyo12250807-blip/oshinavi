import json,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
d=json.load(open('tmp/parsed.json',encoding='utf-8'))
B='https://t.pia.jp/pia/event/event.do?eventBundleCd='
E='https://t.pia.jp/pia/event/event.do?eventCd='
cd={110:'b2665524',128:'b2665378',203:'b2666419',256:'2611766',337:'2620605',
434:'b2668726',438:'2612127',448:'b2667704',468:'b2668129',471:'2609830',
652:'b2562014',658:'2623282',803:'2617640',866:'2615943',978:'2547320',
982:'2614548',988:'2606479',1129:'2622901'}
for i,c in cd.items():
    url=(B+c[1:]) if c.startswith('b') else (E+c)
    print(f"{i}\t{url}")
