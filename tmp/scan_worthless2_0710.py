# -*- coding: utf-8 -*-
"""新着プールから「載せる価値の無い子」を洗い出す（startDateを見て誤判定を防ぐ版）。

罠: startDate==date は「M/D より発売」の単日形＝発売開始日であって締切ではない。
    date だけ見ると「今日が締切」と誤判定して、今日発売開始したばかりの子を消してしまう。
判定:
  実質締切(effective_end) = startDate が無い枠の date（=本当の締切）
  単日形(startDate==date) の枠は「締切不明・まだ生きてる」とみなす
"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TODAY = '2026-07-10'
h = open('index.html', encoding='utf-8').read()
E = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S).group(1))
news = [e for e in E if e.get('genre') == 'new']
print(f'genre:new {len(news)}件\n')

dead, alive_unknown, ok = [], [], []
for e in news:
    ts = e.get('tickets', [])
    url = (e.get('links') or {}).get('pia', '')
    real_ends, single = [], []
    for t in ts:
        sd, d = t.get('startDate'), t.get('date')
        if t.get('saleUntilSoldOut'):
            single.append(t); continue
        if sd and sd == d:
            single.append(t)          # 単日形＝発売開始日。締切は未取込
        elif d:
            real_ends.append(d)       # 本当の締切
    future_real = [d for d in real_ends if d > TODAY]
    future_single = [t for t in single if (t.get('date') or '') >= TODAY]
    row = (e['id'], e['artist'][:26], e.get('venue', '')[:24], e.get('date'), url,
           sorted(real_ends), [t.get('type', '')[:34] for t in single])
    if not future_real and not future_single:
        dead.append(row)                      # 明日には全部死ぬ
    elif not future_real and future_single:
        alive_unknown.append(row)             # 単日形しか無い＝今日発売開始・締切未取込
    else:
        ok.append(row)

print(f'--- 🚨 明日には買える枠ゼロ＝載せる価値なし {len(dead)}件 ---')
for i, a, v, d, u, re_, si in dead:
    print(f'  id={i} {a} @{v} / 公演日 {d}')
    print(f'     締切枠={re_} 単日形={si}')
    if u: print(f'     {u}')
print()
print(f'--- ✅ 今日発売開始・締切未取込（明日のヒールで締切が入る／残す）{len(alive_unknown)}件 ---')
for i, a, v, d, u, re_, si in alive_unknown:
    print(f'  id={i} {a} @{v} / 公演日 {d} / 単日形={si}')
print()
print(f'--- ✅ 将来の締切あり（残す）{len(ok)}件 ---')
print('DEAD_IDS =', [r[0] for r in dead])
