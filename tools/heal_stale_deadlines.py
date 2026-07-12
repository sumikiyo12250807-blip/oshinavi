# -*- coding: utf-8 -*-
"""隠れ枠ヒール（朝ルーチン常設）。

ぴあが「7/3より発売」のような単日形で出す枠は販売終了日が取れず startDate==date で登録される。
index.html renderCard の非表示判定
    if ((!t.startDate || startDate <= today) && date < today) return "";
により、この枠は発売日を過ぎた翌日から**買えるのに画面から消える**。
check_expired.py は「全枠死亡」のエントリしか拾わないため、他に生きた枠があるエントリの中では
永久に埋もれる（2026-07-10 に 96エントリ・149枠が埋もれていた）。

対象 = startDate == date かつ date <= today かつ not saleUntilSoldOut の枠を持つエントリ。
ぴあを再パースして正しい締切を取り込む。買える枠ゼロなら削除候補として報告（自動削除はしない）。

  python tools/heal_stale_deadlines.py            # 走査のみ（規模を出す）
  python tools/heal_stale_deadlines.py --build    # ぴあ再パース → tmp/heal_stale.json
  python tools/heal_stale_deadlines.py --apply    # 上記jsonを index.html に適用（tickets のみ置換）

--ids 154,292 を付けると隠れ枠の有無に関係なくそのエントリを対象にする（期限切れtriageの
救済変換＝「ぴあに買える枠があるのに登録に無い」子の再buildに使う）。

適用は tickets のみ。venue/dateLabel を上書きすると過去のQC手修正（空カッコ会場埋め等）が巻き戻る。
"""
import re, json, sys, io, time, datetime, os

# build_pia_entries も import 時に sys.stdout を包む。ここで TextIOWrapper を二重に被せると
# 先に作ったラッパーが閉じられて "I/O operation on closed file" になる。reconfigure なら安全。
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
OUT = 'tmp/heal_stale.json'
BAK_SUFFIX = 'heal_stale'


def load_events(h):
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    return m, json.loads(m.group(2))


def is_stale(t):
    sd, d = t.get('startDate'), t.get('date')
    return bool(sd and sd == d and d <= TODAY and not t.get('saleUntilSoldOut'))


def pia_urls(ev):
    urls = []
    p = (ev.get('links') or {}).get('pia')
    if p and 'pia' in p:
        urls.append(p)
    for t in ev.get('tickets', []):
        u = t.get('url')
        if u and 'pia' in u and u not in urls:
            urls.append(u)
    return urls


def scan(EVENTS):
    out = []
    for e in EVENTS:
        stale = [t for t in e.get('tickets', []) if is_stale(t)]
        if stale:
            out.append((e, stale))
    return out


def arg_ids():
    if '--ids' not in sys.argv:
        return None
    raw = sys.argv[sys.argv.index('--ids') + 1]
    return [int(x) for x in raw.replace(' ', '').split(',') if x]


def main():
    h = open('index.html', encoding='utf-8').read()
    m, EVENTS = load_events(h)
    ids = arg_ids()
    if ids:
        byid = {e['id']: e for e in EVENTS}
        targets = [(byid[i], []) for i in ids if i in byid]
        # 同日に隠れ枠ヒールも走るので、そちらの成果物/backupを踏まないよう名前を分ける
        global OUT, BAK_SUFFIX
        OUT, BAK_SUFFIX = 'tmp/heal_ids.json', 'rescue'
    else:
        targets = scan(EVENTS)

    if '--apply' in sys.argv:
        if not os.path.exists(OUT):
            print(f'!! {OUT} が無い。先に --build を実行して。'); return
        built = {o['id']: o for o in json.load(open(OUT, encoding='utf-8'))}
        changed = 0
        for e in EVENTS:
            o = built.get(e.get('id'))
            if not o or o.get('status') != 'convert' or not o.get('tickets'):
                continue
            e['tickets'] = o['tickets']
            changed += 1
        left = sum(1 for _, s in scan(EVENTS) for _ in s)
        bak = f'index.html.bak_{datetime.date.today():%m%d}_{BAK_SUFFIX}'
        open(bak, 'w', encoding='utf-8').write(h)
        new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
        open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
        dels = [o for o in built.values() if o.get('status') == 'delete']
        print(f'=== {changed}件 適用 / 残り隠れ枠 {left} (backup: {bak}) ===')
        if dels:
            print(f'\n🚨 買える枠ゼロ = 削除候補 {len(dels)}件（ユーザーOK後に削除）:')
            for o in dels:
                print(f"  id={o['id']} {o.get('artist','')}")
        return

    nslot = sum(len(s) for _, s in targets)
    print(f'=== 隠れ枠スキャン (today={TODAY}) ===')
    print(f'  対象エントリ {len(targets)}件 / 隠れ枠 {nslot}枠')
    for e, s in sorted(targets, key=lambda x: -len(x[1]))[:20]:
        print(f"  id={e['id']:<5} {e.get('artist','')[:28]:<30} 隠れ{len(s)}/全{len(e.get('tickets',[]))}枠")
    if len(targets) > 20:
        print(f'  … 他 {len(targets)-20}件')

    if '--build' not in sys.argv:
        print('\n(走査のみ。ぴあ再パースするなら --build)')
        return

    sys.path.insert(0, 'tools')
    from build_pia_entries import build
    out = []
    for n, (ev, _) in enumerate(targets, 1):
        i = ev['id']
        urls = pia_urls(ev)
        if not urls:
            out.append({'id': i, 'status': 'NO_PIA_URL', 'artist': ev.get('artist', '')})
            print(f'[{n}/{len(targets)}] {i} NO_PIA_URL ⚠️非ぴあ＝要WebFetch'); continue
        try:
            ne = build({'newid': i, 'artist': ev.get('artist', ''), 'urls': urls})
        except Exception as ex:
            out.append({'id': i, 'status': 'ERROR', 'artist': ev.get('artist', ''), 'err': str(ex)[:120]})
            print(f'[{n}/{len(targets)}] {i} ERROR {str(ex)[:60]}'); time.sleep(2.0); continue
        if ne is None:
            out.append({'id': i, 'status': 'delete', 'artist': ev.get('artist', ''), 'urls': urls})
            print(f'[{n}/{len(targets)}] {i} 買える枠ゼロ→削除候補')
        else:
            out.append({'id': i, 'status': 'convert', 'artist': ev.get('artist', ''), 'tickets': ne['tickets']})
            print(f"[{n}/{len(targets)}] {i} convert {len(ne['tickets'])}枠")
        time.sleep(1.2)
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    nc = sum(1 for o in out if o['status'] == 'convert')
    nd = sum(1 for o in out if o['status'] == 'delete')
    print(f'\n=== convert {nc} / 削除候補 {nd} → {OUT} (適用は --apply) ===')


if __name__ == '__main__':
    main()
