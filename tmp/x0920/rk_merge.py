# -*- coding: utf-8 -*-
"""楽天の取りこぼし15件を index.html に入れる（2026-09-20 朝）。

いきさつ＝`build_rakuten_entries` が windows(販売枠)からしか枠を作らず、
windows が空／全部終了のページを「買える枠なし」で丸ごと捨てていた。ビルダーを直して
15件が組み上がったので、ここで入れる。

  新規 4件 …… 既存に相当するものが無い → 新着プール(genre:"new")に投入
  足し込み 11件 … 既存エントリに**楽天の枠だけ**を足し、links.rakuten を入れる
                 🚨楽天は購入ボタン最優先（[[feedback_vendor_priority]]）＝ぴあのあるカードでも足す価値がある。
                 実際、ぴあでは締切済みなのに楽天でまだ買える枠がある（コドモパーティーIII 埼玉＝
                 ぴあ9/17締切／楽天9/26締切）。n.SSign は楽天だけに大阪・福岡・北海道がある。
  🚨同じ（券種名・締切・飛び先）の枠は足さない（画面に同じ badge が2つ並ぶ）。
    飛び先が違うだけの枠は畳まない＝別の売り場（[[feedback_dedup_badges_keeps_urls]]）。
  🚨index.html は CRLF のまま書き戻す（[[feedback_index_html_crlf_preserve]]）。

使い方: python tmp/x0920/rk_merge.py        … 下見
        python tmp/x0920/rk_merge.py --apply
"""
import datetime, io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
APPLY = '--apply' in sys.argv

# 組み上がりの artist名 → 足し込み先の既存id（目で1件ずつ確かめた対応・2026-09-20）
MERGE = {
    '高中正義［追加公演］': 693,
    '【一般視聴チケット】 乃木坂46 42ndSGアンダーライブ': 8382,
    '秦 基博［神奈川］': 3051,
    'n.SSign｜エンサイン ［全国］': 7344,
    'コドモパーティーIII［埼玉・宮城］': 4023,
    'LOVEBITES［全国］': 5501,
    '第38回スタンレーレディスホンダゴルフトーナメント': 2969,
    '【泉佐野市民割・田尻町民割】大阪芸術花火2026': 3239,
    '藤井フミヤ': 1621,
    'ゴールドマン　コレクション　河鍋暁斎の世界［兵庫］': 5487,
}
MERGE_PREFIX = {'世界最大級の大スペクタクル☆スーパーミラクルイリュージョン☆木下大サーカス岡山公演': 9186}

t = io.open('tmp/x0920/rk_built2.txt', encoding='utf-8', errors='replace').read()
built = json.loads(t[t.find('['):])
# 🚨AJAX（公演ごとの売り状態）で「本当に買える」と取れた分だけ入れる（tmp/x0920/rk_buyable.md）。
#   3件（高中正義［追加公演］／秦 基博［神奈川］／アップアップガールズ（フェス）2026）は
#   公演カード/ecd/eid が取れない形式で**確かめられない**＝入れない（[[feedback_no_fake_info]]）。
HOLD = {'高中正義［追加公演］', '秦 基博［神奈川］', 'アップアップガールズ（フェス）2026'}
held = [b for b in built if (b.get('artist') or '').strip() in HOLD]
built = [b for b in built if (b.get('artist') or '').strip() not in HOLD]

raw = io.open('index.html', 'rb').read()
crlf0, lf0 = raw.count(b'\r\n'), raw.count(b'\n')
h = raw.decode('utf-8')
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))
by_id = {e['id']: e for e in events}
maxid = max(e['id'] for e in events)


def target_of(b):
    a = (b.get('artist') or '').strip()
    if a in MERGE:
        return MERGE[a]
    for p, i in MERGE_PREFIX.items():
        if a.startswith(p):
            return i
    return None


added_slots, new_entries, skipped = [], [], []
for b in built:
    tid = target_of(b)
    if tid is None:
        new_entries.append(b)
        continue
    e = by_id[tid]
    have = {(t2.get('type'), t2.get('date'), t2.get('url')) for t2 in (e.get('tickets') or [])}
    for t2 in (b.get('tickets') or []):
        k = (t2.get('type'), t2.get('date'), t2.get('url'))
        if k in have:
            skipped.append((tid, t2.get('type')))
            continue
        if (t2.get('date') or '') < TODAY and not t2.get('soldout'):
            skipped.append((tid, '締切済み: ' + (t2.get('type') or '')))
            continue
        have.add(k)
        added_slots.append((tid, e.get('artist'), t2))
        if APPLY:
            e.setdefault('tickets', []).append(t2)
    if APPLY and not (e.get('links') or {}).get('rakuten'):
        e.setdefault('links', {})['rakuten'] = (b.get('links') or {}).get('rakuten')

# 新規は新着プールへ（genre:"new"）＝ぴあ以外なので振り分けはユーザー確認後
nid = maxid
for b in new_entries:
    nid += 1
    b['id'] = nid
    b['genre'] = 'new'

print('=== 楽天の取りこぼし 投入の下見（today=%s）===' % TODAY)
print('新規 %d件 / 足し込み %d枠 / 足さなかった %d枠' % (len(new_entries), len(added_slots), len(skipped)))
for b in new_entries:
    print('  🆕 id%s %s（公演 %s・枠%d）' % (b['id'], (b.get('artist') or '')[:48],
                                          b.get('date'), len(b.get('tickets') or [])))
for tid, name, t2 in added_slots:
    print('  ＋ id%s %s ｜ %s' % (tid, (name or '')[:30], t2.get('type')))
for tid, why in skipped:
    print('  − id%s %s' % (tid, why))

if not APPLY:
    print('\n(--apply で書き込み)')
    sys.exit(0)

events.extend(new_entries)
# 書き戻しは tools/inject_tiget.py と**同じ型**（CRLFに直してから書く）。
# 🚨ここを我流にすると改行が壊れて sort_guard が誤ブロックする（[[feedback_index_html_crlf_preserve]]）。
NL = '\r\n'
# NEW_ORDER は投入順に足すだけ（並び順は動かさない＝[[feedback_new_list_order_lock]]）
mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
merged = cur + [b['id'] for b in new_entries if b['id'] not in cur]
h2 = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]',
            r'\g<1>' + '[' + ', '.join(map(str, merged)) + ']', h, count=1)
m2 = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)
io.open('index.html.bak_0920_rk', 'w', encoding='utf-8', newline='').write(h)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h2[:m2.start()] + m2.group(1)
    + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', NL)
    + m2.group(3) + h2[m2.end():])

# 突合＝プールとNEW_ORDERが合っているか／改行が壊れていないか
h3 = io.open('index.html', encoding='utf-8', newline='').read()
ev3 = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h3, re.S).group(1))
pool = {x['id'] for x in ev3 if x.get('genre') == 'new'}
arr = set(json.loads(re.search(r'const NEW_ORDER = (\[[^\]]*\])', h3, re.S).group(1)))
raw2 = io.open('index.html', 'rb').read()
print('\nEVENTS %d件 / 新着プール %d件 / NEW_ORDER %d件' % (len(ev3), len(pool), len(arr)))
print('CRCRLF %d / 素のLF %d （どちらも0が正）'
      % (raw2.count(b'\r\r\n'), len(re.findall(rb'(?<!\r)\n', raw2))))
assert arr == pool, '新着プールとNEW_ORDERがズレている'
assert raw2.count(b'\r\r\n') == 0 and not re.findall(rb'(?<!\r)\n', raw2), '改行が壊れた'
print('書き込み完了（バックアップ index.html.bak_0920_rk）')
