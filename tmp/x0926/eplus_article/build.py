import json,sys
sys.stdout.reconfigure(encoding='utf-8')
ev=json.load(open('events.json',encoding='utf-8'))
by={e['id']:e for e in ev}
amz=by[6284]['links']['amazon']
U1='https://eplus.jp/sf/detail/0236750001-P0030449P021001'
U2='https://eplus.jp/sf/detail/0520940001-P0030048P021001'
out=[
 {"id":24300,"artist":"SCANDAL","name":"SCANDAL","date":"2026-11-28",
  "dateLabel":"2026年11月28日(土) 静岡県 SOUND SHOWER ark","venue":"SOUND SHOWER ark","prefecture":"静岡県",
  "genre":"new","_genre":"jpop","_extraGenres":[],"price":None,
  "links":{"rakuten":None,"lawson":None,"pia":None,"eplus":U1,"amazon":amz},
  "tickets":[{"type":"一般発売（静岡県 11/28公演）10/3 10:00発売","date":"2026-11-27","url":U1,"startDate":"2026-10-03"}],
  "verified":True,"verifiedAt":"2026-09-26"},
 {"id":24301,"artist":"TOTO","name":"TOTO","date":"2027-03-23",
  "dateLabel":"2027年3月23日(火) 東京都 有明アリーナ","venue":"有明アリーナ","prefecture":"東京都",
  "genre":"new","_genre":"yougaku","_extraGenres":[],"price":None,
  "links":{"rakuten":None,"lawson":None,"pia":None,"eplus":U2,"amazon":None},
  "tickets":[{"type":"2次プレオーダー受付（東京都 R9年 3/23公演）〜9/29 23:59","date":"2026-09-29","url":U2,"startDate":"2026-09-17"}],
  "verified":True,"verifiedAt":"2026-09-26"},
]
assert not ({e['id'] for e in out} & set(by))
json.dump(out,open('built.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('ok',len(out),sum(len(e['tickets']) for e in out))
