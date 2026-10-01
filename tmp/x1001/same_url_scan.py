# -*- coding: utf-8 -*-
"""呪物メイト型を探す＝1つのカードの中で「行き先（URL）が同じ」バッジが何枚も並ぶもの
 見るのは画面に出る枠（売切・販売終了の印なし・締切が今日以降）だけ。
 型を分ける：
   A 日付だけ違う（券種名の「〜締切」より前が同じ）＝呪物メイト型
   B 券種名が違う（席種・時間帯が違う）＝まとめると何を買うか分からなくなる型
 → tmp/x1001/same_url_scan.txt"""
import io, json, re, collections, datetime
root = 'C:/Users/user/oshinavi/'
TODAY = datetime.date.today().isoformat()
text = io.open(root + 'index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
E, _ = json.JSONDecoder().raw_decode(text, m.start(1))
VEND = [('pia', 'pia.jp'), ('tiget', 'tiget.net'), ('zaiko', 'zaiko.io'), ('fany', 'fany'), ('livepocket', 'livepocket.jp'),
        ('eplus', 'eplus.jp'), ('rakuten', 'rakuten'), ('ltike', 'l-tike')]
def vend(u):
    return next((k for k, s in VEND if s in (u or '')), 'other')
def head(tp):   # 締切・発売の部分を落とした券種名
    return re.sub(r'[）)][^（）()]*$', '）', tp or '')
def head_nodate(tp):   # さらに（…）の中の日付も落とす＝日付だけ違うかを見る
    return re.sub(r'\d{1,2}/\d{1,2}', 'D', head(tp))
A, B = [], []
for e in E:
    vis = [t for t in e.get('tickets') or [] if t.get('url') and not t.get('soldout') and (t.get('date') or '') >= TODAY]
    g = collections.defaultdict(list)
    for t in vis:
        g[t['url']].append(t)
    for u, ts in g.items():
        if len(ts) < 4:
            continue
        kinds = {head_nodate(t['type']) for t in ts}
        row = (len(ts), e['id'], e.get('genre'), vend(u), e.get('name', '')[:40], u, ts[0]['type'][:60], len(kinds))
        (A if len(kinds) == 1 else B).append(row)
out = io.open(root + 'tmp/x1001/same_url_scan.txt', 'w', encoding='utf-8')
for title, rows in (('A 日付だけ違う（呪物メイト型）', A), ('B 券種名も違う', B)):
    rows.sort(reverse=True)
    c = collections.Counter(r[3] for r in rows)
    out.write(f'=== {title}：{len(rows)}組（カード{len({r[1] for r in rows})}枚）・売り場 {dict(c)} ===\n')
    for r in rows[:60]:
        out.write(f'  {r[0]}枚 id{r[1]} [{r[2]}/{r[3]}] {r[4]} | 例 {r[6]} | 種類{r[7]}\n')
