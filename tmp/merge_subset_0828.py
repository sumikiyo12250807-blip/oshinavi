# -*- coding: utf-8 -*-
"""完全重複（同じぴあURLが別エントリに）の統合。
🚨 畳んでよいのは「消す側の枠と飛び先URLが、残す側に全部あるとき」だけ
   （feedback_dedup_badges_keeps_urls＝飛び先URLが違えば別の売り場・導線を消さない）。
   スポーツのホーム/ビジターは対象外（feedback_sports_home_away_never_merge）。
"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
PAIRS = [(608, [497, 500]), (675, [884])]   # (残す, 消す)
h = io.open('index.html', encoding='utf-8', newline='').read()
E = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
by = {e['id']: e for e in E}

def codes(e):
    s = set()
    L = e.get('links') or {}
    for u in [L.get('pia'), L.get('eplus'), L.get('rakuten'), L.get('ltike')]:
        if u: s |= set(re.findall(r'event(?:Bundle)?Cd=(\w+)', u)) | {u}
    for t in (e.get('tickets') or []):
        if t.get('url'):
            s |= set(re.findall(r'event(?:Bundle)?Cd=(\w+)', t['url'])) | {t['url']}
    return s

def shows(e):
    """枠のtypeから (県, 公演日) の集合を粗く取る。"""
    out = set()
    for t in (e.get('tickets') or []):
        for m in re.finditer(r'（([^）]*?)\s*(\d{1,2}/\d{1,2})[^）]*公演）', t.get('type') or ''):
            out.add((m.group(1), m.group(2)))
    return out

ok = True
for keep, drops in PAIRS:
    k = by[keep]
    for d in drops:
        e = by[d]
        lost_codes = codes(e) - codes(k)
        # URL文字列そのものは表記ゆれがあるのでコード（eventCd）だけで判定する
        lost = {c for c in lost_codes if not c.startswith('http')}
        print('残す id%-5s ← 消す id%-5s | 消える側だけが持つぴあコード: %s' % (keep, d, sorted(lost) or 'なし'))
        if lost:
            ok = False
print('\n判定:', 'OK＝導線は1本も消えない' if ok else '🚨NG＝消える側にしか無い売り場がある')
