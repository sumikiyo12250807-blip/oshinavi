# -*- coding: utf-8 -*-
"""一凛5件を index.html の EVENTS に追記。データを内蔵。書込前に再パース検証。
   結果は短い1行で標準出力（壊れにくいように）。"""
import re, json

SRC = 'index.html'

ENTRIES = [
 {"title":"キラナ生誕バンドワンマン前主催 〜祝われたいSP〜","artist":"一凛","date":"2026-07-18",
  "venue":"渋谷 Club Malcolm","prefecture":"東京",
  "tickets":[{"type":"前売券（東京 7/18公演・一凛 出演）","date":"2026-07-18","price":"","url":"https://tiget.net/events/494297","startTime":""}],
  "genre":"new","verified":True,
  "links":{"pia":"","rakuten":"","eplus":"","lawson":"","official":"https://tiget.net/events/494297"}},
 {"title":"ヤギヌマメイ33歳33組3days生誕祭","artist":"一凛","date":"2026-07-19",
  "venue":"四谷LOTUS","prefecture":"東京",
  "tickets":[{"type":"通常チケット（東京 7/19公演・一凛／AiR 出演）","date":"2026-07-19","price":"","url":"https://tiget.net/events/497610","startTime":""}],
  "genre":"new","verified":True,
  "links":{"pia":"","rakuten":"","eplus":"","lawson":"","official":"https://tiget.net/events/497610"}},
 {"title":"COSMIC+09 〜熱帯逃避行〜","artist":"一凛","date":"2026-07-29",
  "venue":"秋葉原 COSMIC LAB","prefecture":"東京",
  "tickets":[{"type":"前売券（東京 7/29公演・一凛 出演）","date":"2026-07-29","price":"","url":"https://tiget.net/events/502388","startTime":""}],
  "genre":"new","verified":True,
  "links":{"pia":"","rakuten":"","eplus":"","lawson":"","official":"https://tiget.net/events/502388"}},
 {"title":"煮豆さん生誕祭","artist":"一凛","date":"2026-07-25",
  "venue":"堺筋本町 club MERCURY","prefecture":"大阪",
  "tickets":[{"type":"予約・詳細（大阪 7/25公演・一凛 出演）","date":"2026-07-25","price":"","url":"https://x.com/hajimerin_/status/2071742283335266641","startTime":""}],
  "genre":"new","verified":True,
  "links":{"pia":"","rakuten":"","eplus":"","lawson":"","official":"https://x.com/hajimerin_/status/2071742283335266641"}},
 {"title":"一凛 3rdワンマンライブ","artist":"一凛","date":"2026-11-23",
  "venue":"秋葉原 CLUB GOODMAN","prefecture":"東京",
  "tickets":[{"type":"予約開始前（東京 11/23公演）※お昼に前主催あり","date":"2026-11-23","price":"","url":"https://x.com/hajimerin_/status/2071742283335266641","startTime":""}],
  "genre":"new","verified":True,
  "links":{"pia":"","rakuten":"","eplus":"","lawson":"","official":"https://x.com/hajimerin_/status/2071742283335266641"}},
]

def main():
    h = open(SRC, encoding='utf-8').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    if not m:
        print("RESULT: FAIL no-EVENTS")
        return
    arr = json.loads(m.group(2))
    before = len(arr)
    maxid = max(e['id'] for e in arr)
    # 既に一凛が居るなら重複投入しない
    if any(e.get('artist') == '一凛' for e in arr):
        print(f"RESULT: SKIP already-has-hajimerin count={before}")
        return
    newids = []
    for e in ENTRIES:
        maxid += 1
        e['id'] = maxid
        arr.append(e)
        newids.append(maxid)
    new_txt = json.dumps(arr, ensure_ascii=False, indent=2)
    h2 = h[:m.start()] + '  const EVENTS = ' + new_txt + ';' + h[m.end():]
    # NEW_ORDER 追記
    mo = re.search(r'(const NEW_ORDER = )\[([0-9,\s]*)\]', h2)
    cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
    merged = cur + [i for i in newids if i not in cur]
    h2 = h2[:mo.start()] + mo.group(1) + '[' + ', '.join(map(str, merged)) + ']' + h2[mo.end():]
    # 検証
    mv = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)
    arr2 = json.loads(mv.group(2))
    haji = [e for e in arr2 if e.get('artist') == '一凛']
    mo2 = re.search(r'const NEW_ORDER = \[([0-9,\s]*)\]', h2)
    no2 = [int(x) for x in re.findall(r'\d+', mo2.group(1))]
    ok = (len(arr2) == before + 5 and len(haji) == 5 and all(i in no2 for i in newids))
    if not ok:
        print(f"RESULT: FAIL validation count={len(arr2)} haji={len(haji)}")
        return
    open('index.html.bak_0716_hajimerin', 'w', encoding='utf-8').write(h)
    open(SRC, 'w', encoding='utf-8').write(h2)
    print(f"RESULT: OK count={len(arr2)} haji={len(haji)} newids={newids} neworder={no2}")

main()
