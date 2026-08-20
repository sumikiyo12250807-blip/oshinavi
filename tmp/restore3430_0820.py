# -*- coding: utf-8 -*-
"""🚨誤削除した 3430 を復活させ、正しい情報に直す。

経緯：ぴあの eventCd=2630005 が消えたので「公演ごと無くなった」と判断して削除した。
      → 実際は **公演は実在し、チケットはこれから発売**（8/29）だった。
      主催が変わった（ウドーではなく「若い演奏家の為のプロジェクト」）ため、
      ぴあ／e+／ウドー公式のどれを見ても出てこなかっただけ。
      主催の情報サイト「仙台・杜の響きコンサート」が **今日8/20に公演情報を公開**していた。

裏づけ（検証エージェントがチラシ現物まで確認）：
  公演名 榛葉樹人＆今井俊輔 コンサート in 仙台 Vol.4 ～オペラ名曲選 仙台の歌姫と共に～
  2026/10/24(土) 18:30開場 19:00開演 ／ 仙台市宮城野区文化センター パトナホール
  出演 榛葉樹人(T)／今井俊輔(Br)／笈沼甲子(pf)／ゲスト 鈴木麻由子(S)・金沢真衣(Ms)
  料金 全席自由 一般4,000円／学生2,000円
  🎫 発売日 2026年8月29日(土) ／ プレイガイド カワイ仙台・藤崎・チケットぴあ(Pコード 334-344)・杜の響きコンサート
  出典 http://www.morinohibiki.com/bbs/in_vol4_1.html
"""
import io, json, re, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

# ① 削除直前のバックアップへ完全に戻す（削除後は読み取り系しか動かしていない）
shutil.copyfile('index.html.bak_0820_del3430', 'index.html')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

n = 0
for e in EVENTS:
    if e['id'] != 3430:
        continue
    e['artist'] = '榛葉樹人＆今井俊輔 コンサート in 仙台 Vol.4'
    e['name'] = '榛葉樹人＆今井俊輔 コンサート in 仙台 Vol.4'
    e['dateLabel'] = '2026年10月24日(土) 宮城 仙台市宮城野区文化センター パトナホール'
    # ぴあのイベントページは消えている（8/29の発売に合わせて作り直される見込み）。
    # 買い方が分かるのは主催の公演ページなので official に載せる。
    e['links'] = {
        'rakuten': None, 'lawson': None, 'pia': None, 'eplus': None,
        'official': 'http://www.morinohibiki.com/bbs/in_vol4_1.html',
    }
    # 発売時刻はチラシに「8月29日(土) チケット発売開始」としか無い＝時刻は推測しない
    e['tickets'] = [{
        'type': '一般発売（宮城 10/24公演）8/29発売',
        'date': '2026-08-29',
        'startDate': '2026-08-29',
        'url': 'http://www.morinohibiki.com/bbs/in_vol4_1.html',
    }]
    e['verified'] = True
    e['verifiedAt'] = '2026-08-20'
    n += 1
    print('復活 id3430 →', e['artist'])
    print('  発売:', e['tickets'][0]['type'], '/ date=', e['tickets'][0]['date'])
    print('  official:', e['links']['official'])

assert n == 1, '3430 が見つからない'
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('=== 復活 %d件 ===' % n)
