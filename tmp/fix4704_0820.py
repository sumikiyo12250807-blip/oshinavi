# -*- coding: utf-8 -*-
"""4704 タクフェス第14弾『北の島から』＝東京(サンシャイン劇場 12/11〜12/20)の一般発売2枠が
バンドルから落ちていた（独立再照合が「ev.date=12/5 / 実ページ千秋楽=12/20」で検知）。
build_pia_entries で機械構築し直し、tickets / date / dateLabel / venue / prefecture を差し替える。
既存 id は据え置き（新着プールの番号固定ルール）。"""
import io, json, re, sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'tools'))
sys.stdout.reconfigure(encoding='utf-8')
import build_pia_entries as B

URL = "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669977"
built = B.build({"newid": 4704, "artist": "タクフェス第14弾『北の島から』", "urls": [URL]})
io.open('tmp/built4704.json', 'w', encoding='utf-8').write(
    json.dumps(built, ensure_ascii=False, indent=1))
print("=== build 結果 ===")
print("artist :", built.get('artist'))
print("venue  :", built.get('venue'))
print("pref   :", built.get('prefecture'))
print("date   :", built.get('date'))
print("label  :", built.get('dateLabel'))
for t in built.get('tickets') or []:
    print("  -", t.get('type'), "| date=", t.get('date'), "| start=", t.get('startDate'), "|", (t.get('url') or '')[:95])
