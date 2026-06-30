# -*- coding: utf-8 -*-
"""【取りこぼし根絶の常設安全網】登録済みエントリ ⇄ ぴあの今の実態 を機械照合する。

個別バグ(parse失敗/分類ミス/将来のぴあ仕様変更)を1つずつ潰すのではなく、
「最終データとぴあの“買える枠”を突合」して、どんな原因のドロップでも【出口で】炙り出す。

検出するもの:
  - 🚨MISSING : ぴあに「買える枠(受付中/発売前)」があるのに登録tickets(未来分)に無い締切 = 取りこぼし
  - ⚠️DROP    : 修正版ビルダーでも parse_when が解析できない枠(=新しいぴあ表記。即対応要)
  - 💤STALE   : 登録にあるがぴあ側に対応する買える枠が無い(売切/終了/延長で日付ズレ)
  - ❌FETCH   : ぴあページ取得失敗

使い方:
  python tools/reconcile_pia.py --new            # genre:"new" の新着プールだけ(既定の推奨)
  python tools/reconcile_pia.py --ids 1240,1253  # 指定idだけ
  python tools/reconcile_pia.py --all            # links.piaがある全エントリ(重い)
  オプション: --limit N (先頭N件) / --quiet (問題ありだけ表示)

build_pia_entries.py の parse_cards/parse_when を再利用するので、ビルダーを直せば照合も自動で追従する。
朝ルーチン&新着レビュー前に通すのが運用ルール(memory: feedback_harvest_status_by_class / feedback_deadline_extended_after_register)。
"""
import re, sys, json, time, datetime, importlib.util

# build_pia_entries は import時に sys.stdout をUTF-8でラップする。二重ラップを避けるため
# 自前ではラップせず、bpe を読み込んで stdout 設定を一本化する。
_spec = importlib.util.spec_from_file_location('bpe', __file__.replace('reconcile_pia.py', 'build_pia_entries.py'))
bpe = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(bpe)

TODAY = datetime.date.today().isoformat()
ARGS = sys.argv[1:]
def opt(name, default=None):
    if name in ARGS:
        i = ARGS.index(name)
        return ARGS[i + 1] if i + 1 < len(ARGS) and not ARGS[i + 1].startswith('--') else True
    return default

QUIET = '--quiet' in ARGS

def load_events(path='index.html'):
    h = open(path, encoding='utf-8').read()
    m = re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S)
    return json.loads(m.group(1))

def pia_urls(ev):
    """このエントリが参照する全ぴあURL(links.pia + 各ticket.url のうち event.do/ticketInformation)。"""
    urls = []
    p = (ev.get('links') or {}).get('pia')
    if p and 'pia' in p:
        urls.append(p)
    for t in ev.get('tickets', []):
        u = t.get('url')
        if u and 'pia' in u and u not in urls:
            urls.append(u)
    return urls

def pia_buyable(urls):
    """ぴあURL群から買える枠を機械抽出 → [(iso_date, suf, title)]。解析不能はdropsに。"""
    buyable, drops, errs = [], [], []
    seen = set()
    for u in urls:
        try:
            h = bpe.fetch(u)
        except Exception as ex:
            errs.append((u, str(ex)[:60])); continue
        # eventCd無効化/差し替え=「ご確認ください」エラーページ。0カードと区別して大声で出す
        # (2026-06-30 風輪のurlが朝有効→無効化。静かに0枠になり取りこぼす穴を塞ぐ)。
        if bpe.is_error_page(h):
            errs.append((u, '無効URL(ご確認ください)=eventCd削除/差替')); continue
        for r in bpe.parse_cards(h):
            if r['state'] not in ('受付中', '発売前'):
                continue
            suf, iso, sd = bpe.parse_when(r['state'], r['when'])
            key = (iso, r['title'], r['perfdate'])
            if key in seen:
                continue
            seen.add(key)
            if not iso:
                drops.append((r['state'], r['when'], r['title'][:40]))
            else:
                buyable.append((iso, suf, r['title'][:40], r['state']))
        time.sleep(0.25)
    return buyable, drops, errs

def main():
    evs = load_events()
    if opt('--ids'):
        ids = set(int(x) for x in str(opt('--ids')).split(','))
        targets = [e for e in evs if e.get('id') in ids]
    elif '--new' in ARGS:
        targets = [e for e in evs if e.get('genre') == 'new']
    elif '--all' in ARGS:
        targets = [e for e in evs if pia_urls(e)]
    else:
        print('対象を指定して: --new / --ids a,b / --all'); return
    lim = opt('--limit')
    if lim:
        targets = targets[:int(lim)]

    print(f'=== reconcile_pia (today={TODAY}) 対象{len(targets)}件 ===\n')
    n_missing = n_drop = n_stale = n_err = n_ok = 0
    for ev in targets:
        urls = pia_urls(ev)
        if not urls:
            continue
        buyable, drops, errs = pia_buyable(urls)
        # 登録tickets(未来締切のみ=今載ってるはずの枠)
        reg = [t for t in ev.get('tickets', []) if (t.get('date') or '') >= TODAY]
        reg_dates = set(t.get('date') for t in reg)
        pia_dates = set(b[0] for b in buyable)
        missing = [b for b in buyable if b[0] not in reg_dates]   # ぴあにあるが登録に無い締切
        stale = [t for t in reg if t.get('date') not in pia_dates]  # 登録にあるがぴあに無い
        # STALE と 枠数不一致 も必ず表に出す（2026-06-26 839南佳孝/1313w.o.d.が「一致」表示で
        # 隠れてた反省。STALEは自動削除でなくWebFetch要確認のサイン）
        problem = bool(missing or drops or errs or stale or len(reg) != len(buyable))
        if problem:
            tag = '🚨' if missing else ('💤' if stale else ('⚠️' if drops else '❌'))
            print(f'{tag} id={ev["id"]} {ev.get("artist","")[:30]} | 登録{len(reg)}枠 / ぴあ買える{len(buyable)}枠')
            for iso, suf, title, st in missing:
                print(f'    🚨MISSING ぴあに [{st}] {suf} ({iso}) があるが登録に無い | {title}')
                n_missing += 1
            for st, w, title in drops:
                print(f'    ⚠️DROP 解析不能 [{st}] when={w!r} | {title}'); n_drop += 1
            for u, e in errs:
                print(f'    ❌FETCH {e} | {u}'); n_err += 1
            if stale and not QUIET:
                for t in stale:
                    print(f'    💤STALE 登録「{t.get("type","")[:40]}」({t.get("date")}) がぴあの買える枠に無い'); n_stale += 1
        else:
            n_ok += 1
            if not QUIET:
                print(f'✅ id={ev["id"]} {ev.get("artist","")[:24]} | 登録{len(reg)}=ぴあ{len(buyable)} 一致')
    print(f'\n=== 集計: OK {n_ok} / 🚨MISSING {n_missing} / ⚠️DROP {n_drop} / 💤STALE {n_stale} / ❌FETCH {n_err} ===')
    if n_missing or n_drop:
        print('→ 🚨/⚠️ は取りこぼし。該当エントリをぴあ機械パースで枠追加して修正すること。')

if __name__ == '__main__':
    main()
