# -*- coding: utf-8 -*-
"""同名で分裂したエントリを1つに統合する（2026-08-18）。

🚨枠は必ず【足し算】にする。ぴあから作り直した枠だけに置き換えると、
既存の枠（ぴあ混雑で読めなかった分・非ぴあの売り場・パーサーが落とした分）が消える。
実測で 202枠→166枠 と36枠も減ったので、union 方式に変えた。

同一性の判定は slot_code(eventCd|rlsCd|lotRlsCd)＝飛び先の売り場
[[feedback_pia_parser_flattens_slots]] / [[feedback_dedup_badges_keeps_urls]]
"""
import io, json, os, re, sys
sys.path.insert(0, 'tools')
import build_pia_entries as bpe
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
BUILT = {b['id']: b for b in json.load(io.open('tmp/mergebuilt_0818.json', encoding='utf-8-sig'))}
DROP = {int(k): v for k, v in json.load(io.open('tmp/mergedrop_0818.json', encoding='utf-8')).items()}

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}


def key(t):
    """枠の同一性＝【券種名＋締切】。
    券種名には「一般発売（愛知 11/1公演）9/12 10:00発売」のように県・公演日・発売時刻が
    全部入っているので、これが実質の識別子になる。
    🚨slot_code は鍵に使わない：
      ・古い枠は ticket.url が空で code が取れない → 同じ枠が新旧で別物に見えて二重になる
        （MONO NO AWARE が 12→24枠になった）
      ・url が event.do?eventCd= 形だと別公演の枠が同じ code になる
        （kein の神奈川10/7・東京11/22・東京11/23 が1枠に潰れた）
    """
    return '%s|%s' % (t.get('type'), t.get('date'))


removed, rows = [], []
for keep_id, built in sorted(BUILT.items()):
    keep = by.get(keep_id)
    if not keep:
        continue
    members = [keep_id] + DROP.get(keep_id, [])
    # ① 作り直した枠を土台にする（最新の締切・会場表記）
    merged, seen = [], set()
    for t in built['tickets']:
        k = key(t)
        if k in seen:
            continue
        seen.add(k)
        merged.append(t)
    # ② 既存の枠のうち、土台に無いものを足す（消さない）
    kept_extra = 0
    for mid in members:
        e = by.get(mid)
        if not e:
            continue
        for t in (e.get('tickets') or []):
            k = key(t)
            if k in seen:
                continue
            seen.add(k)
            merged.append(t)
            kept_extra += 1
    before = sum(len(by[i].get('tickets') or []) for i in members if i in by)
    # ③ 公演日は「いちばん遅い方」を採る＝まだ買えるのにカードが消えるのを防ぐ
    dates = [by[i].get('date') for i in members if i in by and by[i].get('date')]
    dates.append(built.get('date'))
    newdate = max(d for d in dates if d)
    rows.append((keep_id, keep.get('artist'), before, len(merged), keep.get('date'), newdate,
                 kept_extra, DROP.get(keep_id, [])))
    if APPLY:
        keep['tickets'] = merged
        keep['date'] = newdate
        for f in ('venue', 'prefecture', 'dateLabel'):
            if built.get(f):
                keep[f] = built[f]
        removed += DROP.get(keep_id, [])

print('%-6s %-20s %5s %5s %6s  %-11s→%-11s %s' % ('id', '公演名', '前', '後', '既存維持', 'ev.date', '新date', '畳むid'))
for r in rows:
    mark = '' if r[3] >= r[2] else '  🚨減る'
    print('%-6d %-20s %5d %5d %6d  %-11s→%-11s %s%s'
          % (r[0], (r[1] or '')[:18], r[2], r[3], r[6], r[4], r[5], r[7], mark))
print()
print('合計 %d枠 → %d枠 ／ エントリ %d件を畳む' % (sum(r[2] for r in rows), sum(r[3] for r in rows), len(removed)))

if not APPLY:
    print('（判定のみ。適用は --apply）')
    sys.exit(0)

bak = 'index.html.bak_0818_mergedupes'
if not os.path.exists(bak):
    io.open(bak, 'w', encoding='utf-8', newline='').write(h)

EVENTS = [e for e in EVENTS if e['id'] not in set(removed)]
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]

m2 = re.search(r'(NEW_ORDER\s*=\s*)(\[.*?\])', h2, re.S)
if m2:
    order = [i for i in json.loads(m2.group(2)) if i not in set(removed)]
    h2 = h2[:m2.start()] + m2.group(1) + json.dumps(order) + h2[m2.end():]
    print('NEW_ORDER %d件に更新' % len(order))

io.open('index.html', 'w', encoding='utf-8', newline='').write(h2)
print('=== 適用完了 (backup: %s) ===' % bak)
