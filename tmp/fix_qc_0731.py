# -*- coding: utf-8 -*-
"""7/31 新着プール再チェックで出た機械的な直し。
 ① id2544 ウルトラヒーローズ THE LIVE の千秋楽ズレ（❌QC-EVDATE）
    ev.date=11/1 だが実公演は千葉11/14まで＝まだ買えるのにカードが画面から消える。
    会場列挙にも柏（千葉）が抜けているので実態に合わせる。
 ② 新着プール2件の全角スペース（楽天由来）を半角へ。既存2292件中7件しか全角スペースを使っておらず
    サイトの慣例は半角。id・tickets・並び順は一切触らない（現物編集）。
"""
import re, json, datetime, sys
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))

done = []
for e in E:
    if e['id'] == 2544:
        if e['date'] != '2026-11-01':
            print('!! id2544 の date が想定外:', e['date']); sys.exit(1)
        e['date'] = '2026-11-14'
        e['dateLabel'] = '2026年9月12日(土)〜2026年11月14日(土) 全国ツアー'
        e['venue'] = '全国ツアー（不二羽島文化センター スカイホール／赤穂化成ハーモニーホール 大ホール／電力ホール／柏市民文化会館 大ホール）'
        done.append('2544 千秋楽 11/1→11/14・会場に柏を追加')
    if e['id'] in (3514, 3516):
        for k in ('name', 'artist'):
            v = e.get(k) or ''
            if '　' in v:
                e[k] = v.replace('　', ' ')
                done.append('%d %s 全角スペース→半角: %s' % (e['id'], k, e[k]))

if not done:
    print('!! 変更なし。中止'); sys.exit(1)
for d in done:
    print(' -', d)

bak = 'index.html.bak_%s_qcfix' % datetime.date.today().strftime('%m%d')
open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(E, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('=== 適用 (backup: %s) ===' % bak)
