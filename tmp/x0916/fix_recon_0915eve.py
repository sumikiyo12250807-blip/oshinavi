# -*- coding: utf-8 -*-
"""push 前の照合（reconcile_pia --new・9/15夜）で残った2件を、ぴあの状態の文言どおりに直す（2026-09-15夜）。
根拠＝tools/pia_tickets.py <まとめ> --all --json の statustext（tmp/x0916/pt_9151.json・pt_9383.json）。
  9151 エンジン2026 in 岐阜（b2670270）
    ・登録「一般発売（岐阜 9/26公演）〜9/25 23:59」＝夜楽１（鵜の家 足立・eventCd=2630324）＝ぴあ「予定枚数終了」→ 売り切れの印（消さない）
    ・夜楽２（ラパンアジル・eventCd=2630325）＝販売期間中 〜9/23 23:59 が登録に無い → 足す
  9383 ピクサーの世界展〈9/18～9/20〉（b2666511・eventCd=2608515）
    ・9/20入場分（rlsCd=003）＝「予定枚数終了」→ 売り切れの印
    ・9/19入場分（rlsCd=002）＝「予定枚数終了」で登録に無い → 売り切れの印付きで足す（9/15朝の Chevon と同じ扱い）
売り切れ枠の date は、締切が出ていないので公演日にする（公演日を過ぎたら画面から消える）。改行は CRLF を保つ。
使い方: python tmp/x0916/fix_recon_0915eve.py [--apply]
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
TODAY = '2026-09-15'
P = 'https://t.pia.jp/pia/event/event.do?eventCd=%s'

src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
byid = {e['id']: e for e in events}

e = byid[9151]
t = next(t for t in e['tickets'] if t['type'] == '一般発売（岐阜 9/26公演）〜9/25 23:59')
t['type'] = '一般発売【夜楽１】（岐阜 9/26公演）〜9/25 23:59'
t['url'] = P % '2630324'
t['soldout'] = True
t['soldoutSince'] = TODAY
print('  9151 夜楽１ → 予定枚数終了の印')
if not any('夜楽２' in x['type'] for x in e['tickets']):
    e['tickets'].insert(1, {'type': '一般発売【夜楽２】（岐阜 9/26公演）〜9/23 23:59', 'date': '2026-09-23', 'url': P % '2630325'})
    print('  9151 ＋ 夜楽２（岐阜 9/26公演）〜9/23 23:59')
if 'ラパンアジル' in e['venue'] and '鵜の家 足立' not in e['venue']:
    e['venue'] = e['venue'].replace('（ラパンアジル', '（鵜の家 足立／ラパンアジル')
    print('  9151 会場欄に 鵜の家 足立')

e = byid[9383]
t = next(t for t in e['tickets'] if t['type'].startswith('一般発売[9/20(日)入場分]'))
t['url'] = P % '2608515'
t['soldout'] = True
t['soldoutSince'] = TODAY
print('  9383 9/20入場分 → 予定枚数終了の印')
if not any('9/19(土)入場分' in x['type'] for x in e['tickets']):
    e['tickets'].insert(1, {'type': '一般発売[9/19(土)入場分]（東京 9/19公演）', 'date': '2026-09-19', 'url': P % '2608515',
                            'soldout': True, 'soldoutSince': TODAY})
    print('  9383 ＋ 9/19入場分（予定枚数終了）')

if not APPLY:
    print('（--apply で書き込み）')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
