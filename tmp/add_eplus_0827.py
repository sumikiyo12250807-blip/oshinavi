# -*- coding: utf-8 -*-
"""e+の2件を index.html に追加する（値はすべて e+ の実ページから機械で取ったもの・推測ゼロ）。
   🚨index.html は CRLF。newline='' で読み書きする（feedback_index_html_crlf_preserve）。"""
import json,re,io,sys,shutil
sys.stdout.reconfigure(encoding='utf-8')
P='index.html'
shutil.copy(P,'index.html.bak_0827_eplus_add')
src=io.open(P,encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',src,re.S)
EV=json.loads(m.group(2))
nid=max(e['id'] for e in EV)+1

TAKAIWA={
 "id":nid,"artist":"高岩遼","name":"高岩遼 Billboard Live Tour",
 "date":"2026-11-13",
 "dateLabel":"2026年11月3日(火・祝)〜2026年11月13日(金) 全国ツアー",
 "venue":"全国ツアー（Billboard Live YOKOHAMA／Billboard Live OSAKA）",
 "prefecture":"神奈川・大阪","genre":"jazz","price":None,
 "links":{"rakuten":None,"lawson":None,"pia":None,
          "eplus":"https://eplus.jp/sf/detail/2701050002-P0030003P021001",
          "amazon":"https://www.amazon.co.jp/s?k=%E9%AB%98%E5%B2%A9%E9%81%BC%20CD&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22"},
 "tickets":[
  {"type":"抽選オフィシャル先行（神奈川 11/3 16:00公演）〜8/30 23:59","date":"2026-08-30",
   "url":"https://eplus.jp/sf/detail/2701050002-P0030003P021001"},
  {"type":"抽選オフィシャル先行（神奈川 11/3 19:00公演）〜8/30 23:59","date":"2026-08-30",
   "url":"https://eplus.jp/sf/detail/2701050002-P0030003P021002"},
  {"type":"抽選オフィシャル先行（大阪 11/13 18:00公演）〜8/30 23:59","date":"2026-08-30",
   "url":"https://eplus.jp/sf/detail/2701050002-P0030004P021001"},
  {"type":"抽選オフィシャル先行（大阪 11/13 21:00公演）〜8/30 23:59","date":"2026-08-30",
   "url":"https://eplus.jp/sf/detail/2701050002-P0030004P021002"}],
 "verified":True,"verifiedAt":"2026-08-27"}

AKURUYO={
 "id":nid+1,"artist":"明くる夜の羊","name":"明くる夜の羊",
 "date":"2026-11-22",
 "dateLabel":"2026年11月22日(日) 東京 Spotify O-EAST",
 "venue":"Spotify O-EAST","prefecture":"東京","genre":"jpop","price":None,
 "links":{"rakuten":None,"lawson":None,"pia":None,
          "eplus":"https://eplus.jp/sf/detail/3545710001-P0030037P021001",
          "amazon":"https://www.amazon.co.jp/s?k=%E6%98%8E%E3%81%8F%E3%82%8B%E5%A4%9C%E3%81%AE%E7%BE%8A%20CD&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22"},
 "tickets":[
  {"type":"抽選オフィシャル最速先行（東京 11/22公演）〜9/7 23:59","date":"2026-09-07",
   "url":"https://eplus.jp/sf/detail/3545710001-P0030037P021001"}],
 "verified":True,"verifiedAt":"2026-08-27"}

EV.append(TAKAIWA); EV.append(AKURUYO)
arr=json.dumps(EV,ensure_ascii=False,indent=2)
arr='\n'.join('  '+l if i else l for i,l in enumerate(arr.split('\n')))
out=src[:m.start(2)]+arr+src[m.end(2):]
if '\r\n' in src:
    out=out.replace('\r\n','\n').replace('\n','\r\n')
io.open(P,'w',encoding='utf-8',newline='').write(out)
print('追加 id=%d 高岩遼 / id=%d 明くる夜の羊 / 総%d件'%(TAKAIWA['id'],AKURUYO['id'],len(EV)))
