"""照合で出たズレを直す（9/17 夕方・X前の取りこぼし潰し）
・4307 レッドイーグルス＝会期を 12/13 まで・会場に月寒体育館を足す（ぴあの状態ページ b2670454 で確認＝nepia／札幌市月寒体育館）
・2496 高嶋ちさ子＝会期の終わりを 2/28（沖縄 先行）に／大阪12/11・高知12/12・大分1/16・愛知9/22 は ぴあで「予定枚数終了」＝売り切れの印"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
SOLD = ['一般発売（大阪 12/11公演）〜11/25 23:59', '一般発売（高知 12/12公演）〜11/26 23:59',
        '一般発売（大分 R9年 1/16公演）〜12/24 23:59', '一般発売.（愛知 9/22公演）〜9/21 23:59']
for e in events:
    if e['id'] == 4307:
        e['date'] = '2026-12-13'
        e['dateLabel'] = '2026年9月26日(土)〜2026年12月13日(日) 北海道'
        e['venue'] = 'nepiaアイスアリーナ／札幌市月寒体育館'
    if e['id'] == 2496:
        e['date'] = '2027-02-28'
        e['dateLabel'] = e['dateLabel'].replace('〜2027年2月21日(日)', '〜2027年2月28日(日)')
        n = 0
        for t in e['tickets']:
            if t['type'] in SOLD and not t.get('soldout'):
                t['soldout'] = True
                t['soldoutSince'] = '2026-09-17'
                n += 1
        assert n == 4, n
        print('2496', e['dateLabel'], '印', n)
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
