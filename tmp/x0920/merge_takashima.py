# -*- coding: utf-8 -*-
"""高嶋ちさ子 12人のヴァイオリニストの二重登録を1つに畳む（2026-09-20 夜）。

ユーザーの「高嶋ちさ子って一つにまとめられるよね？」で見に行って見つけた。

  id2496 高嶋ちさ子 12人のヴァイオリニスト コンサートツアー 2026〜2027（全国ツアー・まとめページ）
        └ 一般発売（北海道 R9年 2/23公演）10/30 10:00発売  ← 飛び先URLが空
  id7761 高嶋ちさ子 12人のヴァイオリニスト（北海道 2/23 札幌コンサートホールKitara の単独ページ）
        └ 一般発売（北海道 R9年 2/23公演）10/30 10:00発売  ← 同じ枠・eventCd=2636335 を持つ

＝ツアーのまとめページと個別公演ページで二重登録された型（[[feedback_tour_individual_url_dup]]）。
ツアー・複数会場は1エントリ（[[feedback_tour_consolidate]]）なので id2496 に畳む。
🚨畳む前に、**個別ページのURLを2496の北海道の枠へ焼き込む**（[[feedback_tour_per_ticket_url]]）。
   まとめページより会場別ページのほうが、押した人がその公演に直接たどり着ける。

⚠️「ザワつく!昭和歌謡祭」と「ザワつく!音楽会」は**畳まない**。実ページで確かめたら
   福岡9/12と9/13、宮城11/14と11/15＝**同じ会場で2日連続の別演目**だった。
   名前が似ているだけで別のチケット（[[feedback_harvest_name_dedup_blindspot]]）。

使い方: python tmp/x0920/merge_takashima.py [--apply]
"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
NL = '\r\n'
KEEP, DROP = 2496, 7761

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}
keep, drop = by[KEEP], by[DROP]
solo_url = (drop.get('links') or {}).get('pia')
assert solo_url and 'eventCd=' in solo_url, solo_url


def key(t):
    return (t.get('type'), t.get('date'))


have = {key(t) for t in (keep.get('tickets') or [])}
stamped, added = [], []
for t in (drop.get('tickets') or []):
    if key(t) in have:
        # 同じ枠が2496にもある＝畳む側の飛び先を2496へ焼き込む
        for k in (keep.get('tickets') or []):
            if key(k) == key(t) and not k.get('url'):
                stamped.append(k.get('type'))
                if APPLY:
                    k['url'] = solo_url
        continue
    t = dict(t)
    t.setdefault('url', solo_url)
    have.add(key(t))
    added.append(t)

print('残す id%d「%s」' % (KEEP, (keep.get('artist') or '')[:52]))
print('畳む id%d「%s」（%s）' % (DROP, (drop.get('artist') or '')[:40], drop.get('dateLabel')))
print('\n飛び先を焼き込む %d枠' % len(stamped))
for s in stamped:
    print('  ● %s → %s' % (s, solo_url[-30:]))
print('足す %d枠' % len(added))
for t in added:
    print('  ＋ %s' % t.get('type'))

if not APPLY:
    print('\n(--apply で書き込み)')
    sys.exit(0)

keep.setdefault('tickets', []).extend(added)
EVENTS = [e for e in EVENTS if e['id'] != DROP]
io.open('index.html.bak_0920_takashima', 'w', encoding='utf-8', newline='').write(h)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1)
    + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
    + m.group(3) + h[m.end():])
raw = io.open('index.html', 'rb').read()
assert raw.count(b'\r\r\n') == 0 and not re.findall(rb'(?<!\r)\n', raw), '改行が壊れた'
print('\n書き込み完了（バックアップ index.html.bak_0920_takashima）')
