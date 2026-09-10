# -*- coding: utf-8 -*-
"""id4951 ウルフルズ（12/31 フェスティバルホール）に、いま受付中の枠を足す。

■ なぜ
2026-09-10 のローチケ週スキャンで見つけた層＝
「載っているのに、その週に発売が始まる枠を持っていない」（[[project_big_artist_crosscheck]]）。
id4951 は**登録の2枠が両方とも締切を過ぎていて、画面に出る枠が0**だった。
ローチケには **抽選プレリク先行 9/8 12:00〜9/15 23:59（受付中）** が生きている。

■ 実ブラウザで読んだ事実（2026-09-10）
  ウルフルズ ライブ2026 大晦日にBANZAIやったっていいじゃないか！
  2026/12/31(木) フェスティバルホール（大阪府）[開場]16:00 [開演]17:00 通常席 ￥8,800
  抽選 プレリク先行 2026/9/8(火)12:00 〜 2026/9/15(火)23:59／抽選結果発表 9/18(金)15:00頃
  Lコード 54774
🚨抽選結果発表日を「受付開始」と読み替えない（[[feedback_capture_all_deadlines_on_add]]）。
"""
import io
import json
import re
import sys
from urllib.parse import quote

sys.stdout.reconfigure(encoding='utf-8')

URL = ('https://l-tike.com/order/?gLcode=54774&gPfKey=20260724000002257908'
       '&gEntryMthd=03&gScheduleNo=2&gCarrierCd=08&gPfName='
       + quote('ウルフルズ') + '&gBaseVenueCd=53674')

SLOT = {
    "type": "抽選プレリク先行（大阪 12/31公演）〜9/15 23:59",
    "date": "2026-09-15",
    "url": URL,
}

src = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

target = None
for e in events:
    if e['id'] == 4951:
        target = e
        break
if target is None:
    print('!! id4951 が無い')
    sys.exit(1)

print('id4951 %s / 公演%s' % (target.get('name'), target.get('date')))
print('  いまの枠:')
for t in target.get('tickets') or []:
    print('   - %-50s date=%s' % ((t.get('type') or '')[:50], t.get('date')))

if any((t.get('url') or '') == URL for t in target.get('tickets') or []):
    print('  → 同じURLの枠が既にある。何もしない')
    sys.exit(0)

target.setdefault('tickets', []).append(SLOT)
# 売り場のリンクが無ければローチケを入れる（ぴあ枠は残す）
L = target.setdefault('links', {})
if not L.get('lawson'):
    L['lawson'] = URL
print('  足した枠: %s' % SLOT['type'])

out = (src[:m.start()] + m.group(1)
       + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
io.open('index.html', 'w', encoding='utf-8').write(out)
print('書き込み完了')
