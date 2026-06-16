# -*- coding: utf-8 -*-
"""round2新着49件(805-854,825除く)にジャンル振り分け。両方式はextraGenres付与。完了後NEW_ORDER空リセット。"""
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

G={
 # 確実・単独
 805:('rock',None),808:('rock',None),812:('rock',None),813:('rock',None),814:('rock',None),
 816:('rock',None),824:('rock',None),835:('rock',None),841:('rock',None),851:('rock',None),
 852:('rock',None),854:('rock',None),
 806:('jazz',None),815:('jazz',None),818:('jazz',None),829:('jazz',None),846:('jazz',None),847:('jazz',None),
 830:('jpop',None),834:('jpop',None),837:('jpop',None),839:('jpop',None),844:('jpop',None),853:('jpop',None),
 845:('enka',None),850:('kids',None),
 817:('fes',None),833:('fes',None),
 809:('dento',None),810:('dento',None),
 # 両方式（名前ありペア）
 838:('enka',['owarai']),820:('owarai',['engeki']),821:('classic',['jazz']),843:('classic',['jazz']),
 826:('jazz',['classic']),828:('jazz',['jpop']),827:('enka',['jpop']),849:('jpop',['enka']),
 # 両方式（無名→jpop+rock）
 807:('jpop',['rock']),811:('jpop',['rock']),819:('jpop',['rock']),822:('jpop',['rock']),
 823:('jpop',['rock']),831:('jpop',['rock']),832:('jpop',['rock']),836:('jpop',['rock']),
 840:('jpop',['rock']),842:('jpop',['rock']),848:('jpop',['rock']),
}
src=open('index.html',encoding='utf-8').read()
OLD='"genre": "new",'
done=0
for eid,(g,extra) in G.items():
    idx=src.find('"id": %d,'%eid); assert idx!=-1,'id%d'%eid
    gpos=src.find(OLD,idx); assert gpos!=-1 and gpos-idx<700,'genre id%d'%eid
    ls=src.rfind('\n',0,gpos)+1; indent=src[ls:gpos]
    if extra:
        ex=', '.join('"%s"'%x for x in extra)
        new='"genre": "%s",\n%s"extraGenres": [%s],'%(g,indent,ex)
    else:
        new='"genre": "%s",'%g
    src=src[:gpos]+new+src[gpos+len(OLD):]; done+=1
src,n=re.subn(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]',r'\g<1>[]',src,count=1); assert n==1
open('index.html','w',encoding='utf-8').write(src)
print('振り分け %d件 / NEW_ORDER空リセット'%done)
