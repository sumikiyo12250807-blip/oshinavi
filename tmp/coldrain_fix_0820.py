# -*- coding: utf-8 -*-
"""coldrain が2エントリに割れていたのを1つにまとめる。
  4185 SENDAI GIGS単独（eventCd=2626313）＝ツアーの宮城公演そのもの
  4537 全国ツアー bundle（b2669310）
実ページで宮城11/29の一般発売が eventCd=2626313&rlsCd=001 ＝ 4185 のURLと同一だと確認。
さらに 4537 には **北海道10/21のプレリザーブが抜けていた** ので、bundleから作り直す。
"""
import io, json, sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'tools'))
sys.stdout.reconfigure(encoding='utf-8')
import build_pia_entries as B

built = B.build({"newid": 4537, "artist": "coldrain",
                 "urls": ["https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669310"]})
io.open('tmp/built_coldrain.json', 'w', encoding='utf-8').write(
    json.dumps([built], ensure_ascii=False, indent=1))
print("venue:", built.get('venue'))
print("pref :", built.get('prefecture'), "/ date:", built.get('date'))
for t in built.get('tickets') or []:
    print("  -", t.get('type'), "| date=", t.get('date'), "| url=", (t.get('url') or '')[:70])
