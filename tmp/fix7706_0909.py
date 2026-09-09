# -*- coding: utf-8 -*-
"""id7706 藤井風 ピアノリサイタルの券種名を、売り手(e+)の実ページの文言に合わせる。
実ページ https://eplus.jp/sf/web/live/fujiikaze2026/pianorecital/ticket を自分で開いて確認：
  受付名＝「一般抽選受付」（公式ニュースの「チケット最速受付（抽選）」ではない）
  【受付期間】2026年9月9日(水)12:00～2026年9月23日(水・祝)23:59
  【抽選結果確認】2026年10月3日(土)13:00～ ／【支払期限】2026年10月5日(月)21:00
"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

OLD = 'チケット最速受付（抽選）（東京 11/20〜11/21公演）〜9/23 23:59'
NEW = '一般抽選受付（東京 11/20〜11/21公演）〜9/23 23:59'

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 7706)
t = next(x for x in e['tickets'] if x.get('type') == OLD)
t['type'] = NEW
print('id7706 券種名を差し替え\n  旧: %s\n  新: %s' % (OLD, NEW))

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
out = h[:m.start(2)] + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + h[m.end(2):]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
