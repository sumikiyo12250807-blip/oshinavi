"""11129 わたしの知らない子どもたち＝福岡の回は 7944 にある（同じ枠）→ 大阪・東京の回のエントリに組み直す（2026-09-17 昼）。
前提＝heal_stale_deadlines --ids 11129 --apply 済み（ぴあのまとめページ b2671085 の5枠）。福岡の1枠を外し、会期・会場を大阪・東京に直す。
会場はぴあの状態ページで確認＝大阪ステーションシティシネマ 9/28(月)／新宿ピカデリー 10/5(月)。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
for e in events:
    if e['id'] != 11129:
        continue
    before = [t['type'] for t in e['tickets']]
    e['tickets'] = [t for t in e['tickets'] if '（福岡 9/24公演）' not in t['type']]
    assert len(e['tickets']) == len(before) - 1 == 4, before
    e['date'] = '2026-10-05'
    e['dateLabel'] = '2026年9月28日(月)〜2026年10月5日(月) 大阪・東京'
    e['venue'] = '全国ツアー（大阪ステーションシティシネマ／新宿ピカデリー）'
    e['prefecture'] = '大阪・東京'
    print('\n'.join(t['type'] for t in e['tickets']))
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
