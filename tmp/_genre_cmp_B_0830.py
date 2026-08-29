# -*- coding: utf-8 -*-
import re,json,sys
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
B={
5694:"クラシック/オーケストラ",5695:"演劇/寄席・お笑い",5696:"演劇/寄席・お笑い",5697:"演劇/寄席・お笑い",
5698:"イベント/博覧会・展示会・見本市",5699:"イベント/博覧会・展示会・見本市",5700:"イベント/博覧会・展示会・見本市",
5701:"スポーツ/プロレス",5702:"スポーツ/プロレス",5703:"スポーツ/プロレス",5704:"スポーツ/プロレス",
5705:"スポーツ/プロレス",5706:"スポーツ/プロレス",5707:"スポーツ/プロレス",5708:"スポーツ/プロレス",
5709:"スポーツ/スポーツその他",5710:"スポーツ/スポーツその他",5711:"スポーツ/バスケットボール",
5712:"映画/舞台挨拶",5713:"イベント/子供と楽しむ",5714:"映画/舞台挨拶",5715:"音楽/海外ROCK・POPS",
5716:"音楽/フェスティバル",5717:"音楽/J-POP・ROCK",5718:"音楽/J-POP・ROCK",5719:"演劇/寄席・お笑い",
5720:"イベント/祭り・花火大会",5721:"スポーツ/相撲・武道",5722:"スポーツ/バスケットボール",
5723:"スポーツ/バスケットボール",5724:"イベント/イベントその他",5726:"音楽/J-POP・ROCK",
5727:"音楽/J-POP・ROCK",5728:"音楽/J-POP・ROCK",5729:"音楽/J-POP・ROCK",5730:"演劇/演劇",5731:"映画/舞台挨拶",
}
s=open('index.html',encoding='utf-8').read()
ev=json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\n\s*\]);', s, re.S).group(1))
reg={e['id']:e for e in ev if e.get('genre')=='new'}
bad=0
for i,sub in B.items():
    e=reg.get(i)
    if not e: print("id",i,"not in pool"); continue
    if (e.get('_piaSub') or '') != sub:
        bad+=1
        print(f"MISMATCH id={i} {e.get('artist')[:24]} | 登録 {e.get('_piaSub')} vs 再導出 {sub} | 割当 {e.get('_genre')}")
print(f"=== B群 {len(B)}件中 不一致 {bad}件 ===")
