# -*- coding: utf-8 -*-
"""角野隼斗のNDRエルプフィル公演が2エントリに割れているのを1つに畳む（2026-09-20 夜）。

  id5212 NDRエルプフィルハーモニー管弦楽団／アラン・ギルバート（指揮）／角野隼斗（p）
        … 東京2/21・神奈川2/23の2会場。**各枠に会場別のぴあURLが入っている**
  id6988 アラン・ギルバート指揮 NDRエルプフィルハーモニー管弦楽団／ピアノ:角野隼斗
        … まとめページ(bundle)版。愛知・大阪・福岡・東京2/22も入って会場が多いが、
          **ticket.url が全部空**（[[feedback_build_pia_multiurl_loses_ticket_url]] の型）

ツアー・複数会場は1エントリ（[[feedback_tour_consolidate]]）。
🚨畳む前に url が空の枠へ飛び先を焼き込む（[[feedback_tour_per_ticket_url]]）＝
  6988から持ってくる枠には bundle の URL を入れる。会場別URLが分かっている枠は5212のを使う。
残すのは **id5212**（会場別URLを持っているほう）。6988は畳んだあと配列から外す。

使い方: python tmp/x0920/merge_kadono.py [--apply]
"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
NL = '\r\n'
KEEP, DROP = 5212, 6988

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}
keep, drop = by[KEEP], by[DROP]
bundle = (drop.get('links') or {}).get('pia')
assert bundle and 'eventBundleCd' in bundle, bundle


def key(t):
    return (t.get('type'), t.get('date'))


have = {key(t) for t in (keep.get('tickets') or [])}
added = []
for t in (drop.get('tickets') or []):
    if key(t) in have:
        continue
    t = dict(t)
    if not t.get('url'):
        t['url'] = bundle          # 会場別URLが無い枠は まとめページへ飛ばす（空のままにしない）
    have.add(key(t))
    added.append(t)

print('残す id%d「%s」' % (KEEP, (keep.get('artist') or '')[:52]))
print('畳む id%d「%s」' % (DROP, (drop.get('artist') or '')[:52]))
print('\n足す %d枠（飛び先はまとめページを焼き込む）' % len(added))
for t in added:
    print('  ＋ %s' % t.get('type'))

# 会場と会期を伸ばす
all_d = sorted((t.get('date') or '') for t in (keep.get('tickets') or []) + added)
perfs = re.findall(r'（([^（）]*?)\s[^（）]*公演）', ' '.join(
    (t.get('type') or '') for t in (keep.get('tickets') or []) + added))
prefs = []
for p in perfs:
    for one in p.split('・'):
        if one and one not in prefs:
            prefs.append(one)
new_label = '2027年2月21日(日)〜2027年2月28日(日) ' + '・'.join(prefs)
print('\n公演日 %s → 2027-02-28' % keep.get('date'))
print('dateLabel %s\n        → %s' % (keep.get('dateLabel'), new_label))

if not APPLY:
    print('\n(--apply で書き込み)')
    sys.exit(0)

keep.setdefault('tickets', []).extend(added)
keep['date'] = '2027-02-28'
keep['dateLabel'] = new_label
EVENTS = [e for e in EVENTS if e['id'] != DROP]

io.open('index.html.bak_0920_kadono', 'w', encoding='utf-8', newline='').write(h)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1)
    + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
    + m.group(3) + h[m.end():])
raw = io.open('index.html', 'rb').read()
assert raw.count(b'\r\r\n') == 0 and not re.findall(rb'(?<!\r)\n', raw), '改行が壊れた'
print('\n書き込み完了（バックアップ index.html.bak_0920_kadono）')
