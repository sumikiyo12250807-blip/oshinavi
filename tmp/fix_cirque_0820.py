# -*- coding: utf-8 -*-
"""3674 シルク・ドゥ・ソレイユ「クーザ」東京公演を作り直す。

見つかった問題（2026-08-20・ユーザーの「シルク・ドゥ・ソレイユが出てこない」から芋づるで発覚）:
  ・ぴあは **月ごとに3つのbundle** に分かれている
      b2670058=2月(2/24-2/28) / b2670059=3月(3/1-3/9・3/11-3/20・3/21-3/30)
      b2670110=4月(4/2-4/10・4/11-4/20・4/21-4/25)
  ・登録の links.pia は **2月のbundleだけ**＝3月・4月の枠に飛べない
  ・🚨**「フジテレビダイレクト2次先行」が7期間ぶん受付中（〜9/18 23:59）なのに登録に1枠も無い**
    （登録にあるのは「最速先行（受付終了）」と「セブン-イレブン先行（8/29発売）」だけ）
"""
import io, json, sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'tools'))
sys.stdout.reconfigure(encoding='utf-8')
import build_pia_entries as B

URLS = [
    "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670058",
    "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670059",
    "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670110",
]
built = B.build({"newid": 3674, "artist": "シルク・ドゥ・ソレイユ アース製薬 クーザ 東京公演", "urls": URLS})
io.open('tmp/built_cirque.json', 'w', encoding='utf-8').write(
    json.dumps([built], ensure_ascii=False, indent=1))
print("venue :", built.get('venue'))
print("pref  :", built.get('prefecture'), "/ date:", built.get('date'))
print("枠 %d" % len(built.get('tickets') or []))
for t in built.get('tickets') or []:
    print("  -", t.get('type'), "| date=", t.get('date'), "| start=", t.get('startDate'),
          "|", (t.get('url') or '')[:70])
