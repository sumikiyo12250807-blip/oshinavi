# -*- coding: utf-8 -*-
"""布施明の東京11/12（ＬＩＮＥ ＣＵＢＥ ＳＨＩＢＵＹＡ）を「予定枚数終了」で足す（2026-09-20 夜）。

X投稿の総ざらい（投稿に出すアーティスト名でぴあを引く）で、id1214 布施明に
東京11/12の公演が1枠も無いことが分かった。実ページを叩いたら**売り切れ**だった:

  python tools/pia_statustext.py 2622689
    [予定枚数終了] is-active  … 2026/11/12(木) ＬＩＮＥ ＣＵＢＥ ＳＨＩＢＵＹＡ ( 東京都 )
    [抽選受付終了] is-before  … 同上

🚨売り切れは**消さない・載せる**＝「予定枚数終了」で出し続ける
   （[[feedback_soldout_keep_visible]]／[[feedback_oshinavi_concept]]＝公演がこれからなら
     売切れ・販売終了でも全部載せる）。載せないと、探しに来た人は
   「そんな公演は無い」のか「売り切れた」のか区別がつかない。
🚨値はぴあの実ページの文言から取っている。推測していない。

使い方: python tmp/x0920/add_fuse.py [--apply]
"""
import datetime, io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
APPLY = '--apply' in sys.argv
NL = '\r\n'
URL = 'https://t.pia.jp/pia/event/event.do?eventCd=2622689'

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
e = next(x for x in EVENTS if x['id'] == 1214)

add = [
    {'type': '一般発売（東京 11/12公演）', 'date': '2026-11-12', 'url': URL,
     'soldout': True, 'soldoutSince': TODAY},
    {'type': '先行（東京 11/12公演）', 'date': '2026-11-12', 'url': URL,
     'soldout': True, 'saleEnded': True, 'saleEndedSince': TODAY},
]
have = {(t.get('type'), t.get('date')) for t in (e.get('tickets') or [])}
new = [t for t in add if (t['type'], t['date']) not in have]

print('id1214 %s' % e.get('artist'))
print('  いまの dateLabel: %s' % e.get('dateLabel'))
for t in new:
    print('  ＋ %s（%s）' % (t['type'], '予定枚数終了' if not t.get('saleEnded') else '抽選受付終了→販売終了'))

# 会場に東京を足す（公演日の範囲は 10/3〜2027/3/31 のまま＝11/12はその中）
label = e.get('dateLabel') or ''
if '東京' not in label:
    label2 = re.sub(r'(埼玉・愛知)', r'\1・東京', label) if '埼玉・愛知' in label else label + '・東京'
    print('  dateLabel: %s\n           → %s' % (label, label2))
else:
    label2 = label

if not APPLY:
    print('\n(--apply で書き込み)')
    sys.exit(0)

e.setdefault('tickets', []).extend(new)
e['dateLabel'] = label2
io.open('index.html.bak_0920_fuse', 'w', encoding='utf-8', newline='').write(h)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1)
    + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
    + m.group(3) + h[m.end():])
raw = io.open('index.html', 'rb').read()
assert raw.count(b'\r\r\n') == 0 and not re.findall(rb'(?<!\r)\n', raw), '改行が壊れた'
print('\n書き込み完了（バックアップ index.html.bak_0920_fuse）')
