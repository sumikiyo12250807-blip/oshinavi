# -*- coding: utf-8 -*-
"""4719 ウィーン・ヨハン・シュトラウス管弦楽団＝同じ来日ツアーの福岡(1/6)・愛知(1/8)が
別eventCdで売られていて未登録だった（検証エージェントが発見）。3会場を1エントリに統合する。
横浜 2027/1/3 = 2626356 ／ 福岡 2027/1/6 = 2624186 ／ 愛知 2027/1/8 = 2619132
"""
import io, json, sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'tools'))
sys.stdout.reconfigure(encoding='utf-8')
import build_pia_entries as B

URLS = [
    "https://t.pia.jp/pia/event/event.do?eventCd=2626356",
    "https://t.pia.jp/pia/event/event.do?eventCd=2624186",
    "https://t.pia.jp/pia/event/event.do?eventCd=2619132",
]
built = B.build({"newid": 4719, "artist": "ウィーン・ヨハン・シュトラウス管弦楽団", "urls": URLS})
io.open('tmp/built4719.json', 'w', encoding='utf-8').write(json.dumps(built, ensure_ascii=False, indent=1))
print("artist:", built.get('artist'))
print("venue :", built.get('venue'))
print("pref  :", built.get('prefecture'))
print("date  :", built.get('date'))
print("label :", built.get('dateLabel'))
print("genre :", built.get('_genre'), "/", built.get('_piaSub'))
for t in built.get('tickets') or []:
    print("  -", t.get('type'), "| date=", t.get('date'), "| start=", t.get('startDate'), "| url=", (t.get('url') or '')[:80])
