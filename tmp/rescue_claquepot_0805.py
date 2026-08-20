# -*- coding: utf-8 -*-
"""id2320 claquepot の救済＝ぴあ枠は全終了だが e+ で3公演が受付中（機械確認済 2026-08-05）。
  福岡 8/21公演  一般発売 〜2026/8/20 18:00  受付中
  大阪 8/23公演  一般発売 〜2026/8/22 18:00  受付中  ※未登録の公演（Zepp Osaka Bayside）
  東京 8/25公演  一般発売 〜2026/8/24 18:00  受付中
  愛知 8/11公演  受付終了（Zepp Nagoya）＝載せない
実行: python tmp/rescue_claquepot_0805.py [--apply]
"""
import datetime, json, re, sys

sys.stdout.reconfigure(encoding='utf-8')
apply_ = '--apply' in sys.argv

NEW_TICKETS = [
    {"type": "一般発売（福岡 8/21公演）〜8/20 18:00", "date": "2026-08-20",
     "url": "https://eplus.jp/sf/detail/3253480001-P0030059P021001"},
    {"type": "一般発売（大阪 8/23公演）〜8/22 18:00", "date": "2026-08-22",
     "url": "https://eplus.jp/sf/detail/3253480001-P0030060P021001"},
    {"type": "一般発売（東京 8/25公演）〜8/24 18:00", "date": "2026-08-24",
     "url": "https://eplus.jp/sf/detail/3253480001-P0030057P021001"},
]

idx = 'index.html'
h = open(idx, encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
E = json.loads(m.group(2))
e = [x for x in E if x['id'] == 2320][0]

print('--- 変更前 ---')
print('  venue      =', e.get('venue'))
print('  prefecture =', e.get('prefecture'))
print('  dateLabel  =', e.get('dateLabel'))
for t in e['tickets']:
    print('  枠:', t.get('type'), '|', t.get('date'))

e['tickets'] = NEW_TICKETS
e['venue'] = '全国ツアー（Zepp Fukuoka／Zepp Osaka Bayside／Zepp DiverCity（TOKYO））'
e['prefecture'] = '大阪・東京・福岡'
e['dateLabel'] = '2026年8月21日(金)〜2026年8月25日(火) 全国ツアー'
e['date'] = '2026-08-25'
e.setdefault('links', {})['eplus'] = 'https://eplus.jp/sf/detail/3253480001-P0030057P021001'
e['verifiedAt'] = datetime.date.today().isoformat()

print('--- 変更後 ---')
print('  venue      =', e.get('venue'))
print('  prefecture =', e.get('prefecture'))
print('  dateLabel  =', e.get('dateLabel'))
for t in e['tickets']:
    print('  枠:', t.get('type'), '|', t.get('date'), '|', t.get('url'))

if apply_:
    bak = 'index.html.bak_%s_claquepot' % datetime.date.today().strftime('%m%d')
    open(bak, 'w', encoding='utf-8').write(h)
    new_arr = json.dumps(E, ensure_ascii=False, indent=2)
    open(idx, 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    raw = open(idx, 'rb').read()
    print('=== 適用 (backup: %s) / 孤立LF=%d ===' % (bak, raw.count(b'\n') - raw.count(b'\r\n')))
else:
    print('=== 表示のみ。適用は --apply ===')
