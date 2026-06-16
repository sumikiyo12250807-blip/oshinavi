# -*- coding: utf-8 -*-
"""round2の修正: 832補完・852発売前枠追加・838会場別分割・825削除。all_new2.json生成。"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

allnew=[]
for f in ['tmp/g2_A.json','tmp/g2_B.json','tmp/g2_C.json','tmp/g2_D.json']:
    allnew+=json.load(open(f,encoding='utf-8'))
by={e['id']:e for e in allnew}

# 825 パンタレイ 削除（空tickets・公演間近）
allnew=[e for e in allnew if e['id']!=825]

# 832 ふたりエッヂ 補完
allnew.append({
 "id":832,"artist":"ふたりエッヂ","name":"ふたりエッヂ","date":"2026-08-29",
 "dateLabel":"2026年8月29日(土) 北海道","venue":"SPIRITUAL LOUNGE","prefecture":"北海道",
 "genre":"new","price":None,
 "links":{"rakuten":None,"lawson":None,"pia":"https://t.pia.jp/pia/event/event.do?eventCd=2623880","eplus":None,"amazon":None},
 "tickets":[{"type":"一般発売（北海道 8/29公演）6/21 10:00発売","startDate":"2026-06-21","date":"2026-06-21"}],
 "verified":True,"verifiedAt":"2026-06-16"})

# 852 LINDBERG 発売前プレリザーブ追加
by852=next(e for e in allnew if e['id']==852)
by852['tickets']=[{"type":"プレリザーブ（北海道 12/10・12/12公演）6/20 12:00発売","startDate":"2026-06-20","date":"2026-06-20"}]

# 838 美川/コロッケ 会場別5公演に分割＋詳細URL
TI="https://t.pia.jp/pia/ticketInformation.do?eventCd=2622919&rlsCd=001"
by838=next(e for e in allnew if e['id']==838)
by838['links']['pia']=TI
by838['date']="2026-11-25"
by838['dateLabel']="2026年11月11日〜25日 全国ツアー"
by838['prefecture']="茨城・埼玉・三重・岐阜"
by838['tickets']=[
 {"type":"一般発売（茨城 11/11公演）6/25 10:00発売","startDate":"2026-06-25","date":"2026-06-25"},
 {"type":"一般発売（埼玉 11/17公演）6/25 10:00発売","startDate":"2026-06-25","date":"2026-06-25"},
 {"type":"一般発売（三重 11/19公演）6/25 10:00発売","startDate":"2026-06-25","date":"2026-06-25"},
 {"type":"一般発売（岐阜 11/20公演）6/25 10:00発売","startDate":"2026-06-25","date":"2026-06-25"},
 {"type":"一般発売（埼玉 11/25公演）6/25 10:00発売","startDate":"2026-06-25","date":"2026-06-25"},
]

allnew.sort(key=lambda e:e['id'])
json.dump(allnew,open('tmp/all_new2.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
empty=[e['id'] for e in allnew if not e['tickets']]
print("最終:",len(allnew),"件 / 空tickets:",empty or "なし")
print("id:",sorted(e['id'] for e in allnew))
PY=0
PY
