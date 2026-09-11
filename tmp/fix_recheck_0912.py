# -*- coding: utf-8 -*-
"""前夜の新着の再チェック（別エージェント4本のゼロ再導出）で出た本物のズレを直す（2026-09-12 朝）。
根拠はどれも、あたしがぴあの生ページを読み直したもの（tmp/*_0912.txt ／ tmp/*_2627549.txt ほか）。

  7933 天皇杯 9/23 … 枠は6会場（大阪・京都・東京・兵庫・千葉・茨城）あるのに、県と会場名が4つだけ
                     → 5県以上は「全国」（build_pia_entries と同じ規則）・会場名を6つに
  7959 THAI ON FESTIVAL … 今日9/12の当日券（〜9/12 20:00）が受付中なのに登録に無い → 足す
  7975 トップシークレットマン … 9/19 東京 Spotify O-WEST（これからの公演・受付は終了）が会期から抜けていた
  8009 BELLE & SEBASTIAN … 9/22 大阪 BIGCAT・9/25 東京（これからの公演・受付は終了）が会期から抜けていた
  ※会期は事実で書く（memory feedback_show_true_dates_not_sellable_range）。prefecture は「買える県」のまま
    （7882・8145 と同じ扱い）。予定枚数終了・受付終了の枠は新規には足さない。
使い方: python tmp/fix_recheck_0912.py [--apply]
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 🚨改行の作法＝読みも書きも既定のまま（newline を指定しない）＝CRLFが往復で保たれる
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}


def setf(i, k, old, new):
    e = by[i]
    assert e.get(k) == old, 'id%s %s が想定と違う: %r' % (i, k, e.get(k))
    e[k] = new
    print('id%-5s %-10s %s\n             → %s' % (i, k, old, new))


# 7933 天皇杯
setf(7933, 'prefecture', '大阪・京都・東京・兵庫', '全国')
setf(7933, 'dateLabel', '2026年9月23日(水) 大阪・京都・東京・兵庫 パナソニックスタジアム吹田', '2026年9月23日(水) 全国')
setf(7933, 'venue', '全国ツアー（パナソニックスタジアム吹田／サンガスタジアム by KYOCERA／町田GIONスタジアム／ノエビアスタジアム神戸）',
     '全国ツアー（パナソニックスタジアム吹田／サンガスタジアム by KYOCERA／町田GIONスタジアム／ノエビアスタジアム神戸／三協フロンテア柏スタジアム／メルカリスタジアム）')

# 7959 THAI ON FESTIVAL＝今日の当日券
t_new = {'type': '当日券発売（東京 9/12公演）〜9/12 20:00', 'date': '2026-09-12'}
assert not any(t.get('type') == t_new['type'] for t in by[7959]['tickets']), '7959 はもう足してある'
by[7959]['tickets'].append(t_new)
print('id7959  ＋%s' % t_new['type'])

# 7975 トップシークレットマン
setf(7975, 'dateLabel', '2026年9月25日(金) 大阪 Live House Anima', '2026年9月19日(土)〜2026年9月25日(金) 東京・大阪')
setf(7975, 'venue', 'Live House Anima', '全国ツアー（Spotify O-WEST／Live House Anima）')

# 8009 BELLE & SEBASTIAN
setf(8009, 'date', '2026-09-24', '2026-09-25')
setf(8009, 'dateLabel', '2026年9月24日(木) 東京 Kanadevia Hall', '2026年9月22日(火)〜2026年9月25日(金) 大阪・東京')
setf(8009, 'venue', 'Kanadevia Hall', '全国ツアー（BIGCAT／Kanadevia Hall）')

if '--apply' not in sys.argv:
    print('\n(--apply で書き込み)')
    sys.exit(0)
open('index.html', 'w', encoding='utf-8').write(
    src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
print('書き込み完了')
