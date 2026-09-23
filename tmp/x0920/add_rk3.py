# -*- coding: utf-8 -*-
"""楽天で「機械では確かめられなかった3件」を、実ページを開いて読んだ値で入れる（2026-09-20 朝）。

3件とも `rakuten_perf_status` が「公演カード/ecd/eidが取れない形式」で判定できず、
ビルダーのフォールバックは**カードの販売終了日時**（公演前日）を締切にしていた＝嘘だった。
実ページの「販売期間」を読んだら次のとおり:

  ✅高中正義［追加公演］ 12/31 東京 Zepp Haneda
      販売期間「高中正義公式ホームページ1次最速先行」2026/09/17 18:00 〜 2026/09/30 23:59 … 受付中
      （ビルダーは「〜9/30 23:59」を出していたので締切は合っていた。券種名だけ直す）
  ✅秦 基博［神奈川］ 11/8 ぴあアリーナ MM
      販売期間「2次先行抽選」2026/09/07 12:00 〜 2026/09/23 23:59 … 受付中
      🚨ビルダーは「〜11/7 23:59」＝**1か月半も長い嘘**を出していた
  ❌アップアップガールズ（フェス）2026 11/21 BLAZE GOTANDA
      販売期間「楽天チケット先行」2026/08/28 18:00 〜 2026/09/07 23:59 … **もう終わっている**
      ＝載せない（ビルダーは「〜11/20 23:59」の嘘を出していた）

🚨値は実ページの文字をそのまま写している。推測していない（[[feedback_no_fake_info]]）。
使い方: python tmp/x0920/add_rk3.py [--apply]
"""
import io, json, re, sys, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
NL = '\r\n'


def deeplink(u):
    return ('https://click.linksynergy.com/deeplink?id=z9x6HLNpWco&mid=53531&murl='
            + urllib.parse.quote(u, safe=''))


ADD = [
    (693, 'https://ticket.rakuten.co.jp/music/jpop/rtol231/',
     {'type': '高中正義公式ホームページ1次最速先行（東京 12/31公演）〜9/30 23:59',
      'date': '2026-09-30'}),
    (3051, 'https://ticket.rakuten.co.jp/music/rtst020/',
     {'type': '2次先行抽選（神奈川 11/8公演）〜9/23 23:59',
      'date': '2026-09-23'}),
]

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}

for eid, url, t in ADD:
    e = by[eid]
    t = dict(t, url=deeplink(url))
    have = {(x.get('type'), x.get('date')) for x in (e.get('tickets') or [])}
    print('== id%d %s' % (eid, (e.get('artist') or '')[:40]))
    if (t['type'], t['date']) in have:
        print('   既にある＝足さない')
        continue
    print('   ＋ %s' % t['type'])
    if APPLY:
        e.setdefault('tickets', []).append(t)
        if not (e.get('links') or {}).get('rakuten'):
            e.setdefault('links', {})['rakuten'] = deeplink(url)
            print('   links.rakuten を入れた（購入ボタンは楽天が最優先）')

if not APPLY:
    print('\n(--apply で書き込み)')
    sys.exit(0)

io.open('index.html.bak_0920_rk3', 'w', encoding='utf-8', newline='').write(h)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1)
    + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
    + m.group(3) + h[m.end():])
raw = io.open('index.html', 'rb').read()
assert raw.count(b'\r\r\n') == 0 and not re.findall(rb'(?<!\r)\n', raw), '改行が壊れた'
print('\n書き込み完了（バックアップ index.html.bak_0920_rk3）')
