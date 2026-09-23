# -*- coding: utf-8 -*-
"""TIGETの「二重登録疑い」7件を、中身を1件ずつ見て入れる（2026-09-20 昼）。

🚨結論＝**7件とも二重登録ではなかった**。飛び先のTIGETイベントidが全部違う＝別の売り場。
   [[feedback_dedup_badges_keeps_urls]]（飛び先が違えば畳まない）／
   [[feedback_oshinavi_concept]]（推しに会いに行ける枠は全部載せる）。

  ① NoGoD → id6016（e+のツアー5会場）
     TIGETは1会場1ページで10本ある。**うち5会場（11/14東京・11/20神奈川・11/29愛知・
     12/4大阪・12/5兵庫／どれも10/3 10:00発売）は、うちに1枠も無い**＝純粋な取りこぼし。
     残り5会場は e+ と同じ公演なので足さない（画面に見分けのつかないバッジが並ぶだけ）。
  ② GA-HA-他 → id13069（11/21の1枠だけ）
     TIGETは 11/21 がもう1ページ（495331≠495329＝別の部）と、**11/22 が丸ごと未登録**。
  ③ 一凛 → id2764
     既存の枠は「予約開始前」でXのURL＝**買えない**。TIGETが本物の売り場。
  ④ 竹内大規他 → id11757（9/21）
     同じ日に3ページ（12:20／12:34／13:14発売）＝別の部。登録は13:14の1本だけ。
  ⑤ 大祀/DAISHI → id13704（9/26）
     既存は『音楽的自由奔放祭Vol.27』、新は『Bistro☆DAISHI4』＝**別のイベント**。
  ⑥ 空飛ぶリビング他 → id12578（10/11）
     既存は単日券、新は**通し券**＝別の券種。

🚨index.html は CRLF のまま書き戻す。
使い方: python tmp/x0920/add_tiget7.py [--apply]
"""
import datetime, io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
APPLY = '--apply' in sys.argv
NL = '\r\n'

# (組み上がりの artist名, 足し込み先id, 入れる公演日の条件)
#   None＝その名前の組み上がりを全部入れる／set＝その公演日だけ入れる
PLAN = [
    ('NoGoD', 6016, {'2026-11-14', '2026-11-20', '2026-11-29', '2026-12-04', '2026-12-05'}),
    # 🚨11/21は既存と券種名が一字一句同じ＝画面に見分けのつかないバッジが2つ並ぶので入れない。
    #   11/22は丸ごと未登録＝入れる。
    ('GA-HA-／モリナオフミ（フラチナリズム）／KEN EBISAWA', 13069, {'2026-11-22'}),
    ('一凛', 2764, None),
    ('竹内大規／電車／パンマーなけうち', 11757, None),
    ('大祀/DAISHI(天照、Neu:NOIZ)', 13704, None),
    ('空飛ぶリビング／町田恐怖症／ビッシャビシャカラス', 12578, None),
]

built = json.load(io.open('tmp/x0919/built_tiget_rest.json', encoding='utf-8'))['entries']
h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}

added = []
for name, eid, only in PLAN:
    e = by[eid]
    have = {(t.get('type'), t.get('date'), t.get('url')) for t in (e.get('tickets') or [])}
    for b in built:
        if (b.get('artist') or '').strip() != name:
            continue
        if only is not None and b.get('date') not in only:
            continue
        for t in (b.get('tickets') or []):
            k = (t.get('type'), t.get('date'), t.get('url'))
            if k in have:
                continue
            if (t.get('date') or '') < TODAY and not t.get('soldout'):
                continue
            have.add(k)
            added.append((eid, name, b.get('date'), t))
            if APPLY:
                e.setdefault('tickets', []).append(t)
                # ツアーは1エントリ＝千秋楽まで伸ばす（[[feedback_tour_consolidate]]）
                if (b.get('date') or '') > (e.get('date') or ''):
                    e['date'] = b['date']

print('=== TIGETの7件を入れる（today=%s）===' % TODAY)
print('足す %d枠' % len(added))
for eid, name, d, t in added:
    print('  ＋ id%s %s（公演 %s）｜ %s' % (eid, name[:24], d, t.get('type')))
if not APPLY:
    print('\n(--apply で書き込み)')
    sys.exit(0)

io.open('index.html.bak_0920_tiget7', 'w', encoding='utf-8', newline='').write(h)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1)
    + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
    + m.group(3) + h[m.end():])
raw = io.open('index.html', 'rb').read()
assert raw.count(b'\r\r\n') == 0 and not re.findall(rb'(?<!\r)\n', raw), '改行が壊れた'
print('\n書き込み完了（バックアップ index.html.bak_0920_tiget7）')
