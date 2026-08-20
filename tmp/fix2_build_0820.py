# -*- coding: utf-8 -*-
"""push直前の照合で出た2件を作り直す。
 4762 博品館劇場「シャーロック・ホームズ」＝ぴあに「受付中〜8/26 23:59」のプレ枠があるのに登録に無い
 4765 スターダンサーズ・バレエ団「くるみ割り人形」＝ぴあが混雑ページを返した巻き添えでSTALE判定
       （[[reference_pia_rate_limit_429]]＝FETCH付きのSTALEは本物とは限らない）→ 取り直して確認する
URLは index.html から機械抽出したもの（捏造しない）。
"""
import io, json, sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'tools'))
sys.stdout.reconfigure(encoding='utf-8')
import build_pia_entries as B

JOBS = [
    (4762, "博品館劇場名作リーディングシアター「シャーロック・ホームズ～緋色の研究・出会い～」",
     "https://t.pia.jp/pia/event/event.do?eventCd=2631662"),
    (4765, "スターダンサーズ・バレエ団公演「くるみ割り人形」全2幕（神奈川公演）",
     "https://t.pia.jp/pia/event/event.do?eventCd=2633150"),
]
out = []
for nid, artist, url in JOBS:
    try:
        e = B.build({"newid": nid, "artist": artist, "urls": [url]})
    except Exception as ex:
        print("id%d 取得失敗: %s" % (nid, ex))
        continue
    out.append(e)
    print("id%d %s / date=%s / 枠%d" % (nid, e.get('venue'), e.get('date'), len(e.get('tickets') or [])))
    for t in e.get('tickets') or []:
        print("   -", t.get('type'), "| date=", t.get('date'), "| start=", t.get('startDate'))

io.open('tmp/built_fix2.json', 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1))
