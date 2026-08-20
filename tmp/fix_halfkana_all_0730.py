"""既存データの半角カナを全角化する（表示テキストだけ・URLやdateは触らない）。
2026-07-30の目視で発覚＝楽天由来(ｽﾎﾟｰﾂﾊﾟｰｸ/ﾋﾞﾚｯｼﾞﾎｰﾙ/Cｹﾞｰﾄ/ﾓｴﾚ)とe+由来(半角中黒 ･)。
ビルダー側は同日 fix_half_kana() で恒久修正済み（build_rakuten_entries / eplus_harvest）。
半角カナの連続だけ NFKC する＝全角ラテンや（）／〜には触らない最小限の正規化。

  python tmp/fix_halfkana_all_0730.py            # 差分表示のみ
  python tmp/fix_halfkana_all_0730.py --apply
"""
import json
import re
import sys
import unicodedata

APPLY = '--apply' in sys.argv
HALF = re.compile(r'[｡-ﾟ]+')


def fix(s):
    if not isinstance(s, str) or not s:
        return s
    return HALF.sub(lambda m: unicodedata.normalize('NFKC', m.group(0)), s)


h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))

out, n_ev, n_field = [], 0, 0
for e in EVENTS:
    hit = []
    for k in ('artist', 'name', 'venue', 'dateLabel'):
        v = e.get(k)
        nv = fix(v)
        if nv != v:
            hit.append('  %s: %s → %s' % (k, v, nv))
            e[k] = nv
            n_field += 1
    for i, t in enumerate(e.get('tickets') or [], 1):
        v = t.get('type')
        nv = fix(v)
        if nv != v:
            hit.append('  枠%d.type: %s → %s' % (i, v, nv))
            t['type'] = nv
            n_field += 1
    if hit:
        n_ev += 1
        out.append('id%s (genre=%s) %s' % (e.get('id'), e.get('genre'), e.get('name')))
        out += hit

out.insert(0, '半角カナを直したエントリ %d件 / フィールド %d箇所' % (n_ev, n_field))

if APPLY and n_ev:
    open('index.html.bak_0730_halfkana', 'w', encoding='utf-8').write(h)
    # CRLF保護＝読みは universal newlines・書きは text モード（newline='' を使わない）
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    out.append('=== 適用した (backup: index.html.bak_0730_halfkana) ===')
else:
    out.append('=== 表示のみ。適用するなら --apply ===')

open('tmp/fix_halfkana_all_0730.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('wrote tmp/fix_halfkana_all_0730.txt (entries=%d fields=%d apply=%s)' % (n_ev, n_field, APPLY))
