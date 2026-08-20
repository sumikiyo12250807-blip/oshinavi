# -*- coding: utf-8 -*-
"""前進座創立95周年記念公演『出雲の阿国』が2エントリに割れていたのを1つにまとめる。
  3163 大阪・国立文楽劇場 10/8〜10/11 （eventCd=2621248）
  3552 東京・三越劇場     10/17〜10/24（eventCd=2629415）
実ページで演目が両方とも『出雲の阿国』・出演も同じ一座であることを確認済み＝同じ興行の巡演。
id は小さい 3163 に寄せ、3552 は統合後に削除する（[[feedback_tour_consolidate]]）。
"""
import io, json, sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'tools'))
sys.stdout.reconfigure(encoding='utf-8')
import build_pia_entries as B

URLS = ["https://t.pia.jp/pia/event/event.do?eventCd=2621248",
        "https://t.pia.jp/pia/event/event.do?eventCd=2629415"]
built = B.build({"newid": 3163, "artist": "前進座創立95周年記念公演 『出雲の阿国』", "urls": URLS})
io.open('tmp/built_zenshinza.json', 'w', encoding='utf-8').write(
    json.dumps([built], ensure_ascii=False, indent=1))
print("artist:", built.get('artist'))
print("venue :", built.get('venue'))
print("pref  :", built.get('prefecture'), "/ date:", built.get('date'))
print("label :", built.get('dateLabel'))
for t in built.get('tickets') or []:
    print("  -", t.get('type'), "| date=", t.get('date'), "| url=", (t.get('url') or '')[:70])
