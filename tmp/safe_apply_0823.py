# -*- coding: utf-8 -*-
"""ヒールの安全弁で適用できなかった10件を、全URLからの再導出結果で**足すだけ**当てる。

なぜ heal --apply が止まったか＝heal は tickets を丸ごと置き換える設計で、
まとめページ(bundle)からの再導出だけだと**生きている枠が消える**（[[feedback_pia_bundle_hides_shows]]）。
→ 統合と同じやり方にする＝エントリに紐づく**全URL**を渡して再導出し、**増えた枠だけ足す**。

古い「8/22 10:00発売」形の枠（締切が入っていない隠れ枠）は消さない。
日付が過ぎていて画面には出ないので実害はなく、消すと元に戻せない。
"""
import re, io, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
TODAY = datetime.date.today().isoformat()

built = {e['id']: e for e in json.load(io.open('tmp/safe_built_0823.json', encoding='utf-8'))}
h = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}


def key(t):
    return (t.get('type'), t.get('date'))


log = io.open('tmp/safe_diff_0823.txt', 'w', encoding='utf-8')
added = touched = 0
for i, b in sorted(built.items()):
    e = by.get(i)
    if e is None:
        log.write('!! id%s が index に無い\n' % i)
        continue
    old = e.get('tickets') or []
    have = {key(t) for t in old}
    new = [t for t in b['tickets'] if key(t) not in have]
    if not new:
        log.write('== id%-5d %s : 増えた枠なし（登録%d枠）\n' % (i, e.get('name', ''), len(old)))
        continue
    touched += 1
    added += len(new)
    log.write('== id%-5d %s : 枠 %d → %d\n' % (i, e.get('name', ''), len(old), len(old) + len(new)))
    for t in new:
        log.write('   + %s | %s | %s\n' % (t['type'], t.get('date'), t.get('url') or '-'))
    if APPLY:
        for t in old:
            t.setdefault('url', (e.get('links') or {}).get('pia'))
        e['tickets'] = old + new
        if b.get('date') and b['date'] > (e.get('date') or ''):
            e['date'] = b['date']
            for f in ('dateLabel', 'venue', 'prefecture'):
                if b.get(f):
                    e[f] = b[f]
        e['verifiedAt'] = TODAY

# 同じ文言のバッジが「どちらも画面に出る状態」で並んでいないか
for i in built:
    e = by.get(i)
    if not e:
        continue
    live = [t.get('type') for t in e['tickets'] if (t.get('date') or '') >= TODAY]
    dup = [x for x in set(live) if live.count(x) > 1]
    if dup:
        log.write('🚨 SAME-BADGE(表示中) id%d: %s\n' % (i, dup))

log.write('\n=== 枠が増えたエントリ %d件 / 追加 %d枠 ===\n' % (touched, added))
log.close()
print('枠が増えたエントリ %d件 / 追加 %d枠 → tmp/safe_diff_0823.txt' % (touched, added))

if APPLY:
    io.open('index.html.bak_0823_safeheal', 'w', encoding='utf-8').write(h)
    io.open('index.html', 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
    print('適用した')
else:
    print('（見ただけ。適用は --apply）')
