# -*- coding: utf-8 -*-
"""出演者の欄を売り場から取り直す（2026-10-26 新設・gate_fields M の直し方）。

  python tools/refetch_artist.py --ids 1,2,3            … 下見
  python tools/refetch_artist.py --ids 1,2,3 --apply    … 書く
  python tools/refetch_artist.py --pool [--apply]        … 新着プールで M に出た分

読む所＝ぴあ「出演者など」の［出演］（build_pia_entries.pia_cast）／e+ アーティストのリンク（eplus_harvest.eplus_artists）。
TIGET・ZAIKO・FANY・livePocket はそれぞれの組み立てが出演者を持つ＝ここでは読まない（報告だけ）。
読めない・空の時は触らない（公演名のまま＝推測で名前を作らない）。
"""
import io, json, re, sys, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_pia_entries as BP   # noqa: E402
import eplus_harvest as EH       # noqa: E402
import gate_fields as GF         # noqa: E402

ROOT = 'C:/Users/user/oshinavi/'
import datetime  # noqa: E402
TODAY_S = datetime.date.today().isoformat()
NOCAST = {}
CHECKED_F = ROOT + 'tools/artist_castcheck.json'
try:
    CHECKED = json.load(io.open(CHECKED_F, encoding='utf-8'))
except FileNotFoundError:
    CHECKED = {}


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    apply = '--apply' in sys.argv
    s = io.open(ROOT + 'index.html', encoding='utf-8', newline='').read()
    mm = re.search(r'const\s+EVENTS\s*=\s*(\[)', s)
    st = mm.start(1)
    E, end = json.JSONDecoder().raw_decode(s, st)
    if '--pool' in sys.argv:
        ok = GF._artist_ok()
        ids = {e['id'] for e in E if e.get('genre') == 'new' and GF.artist_looks_like_title(e, ok)}
    else:
        ids = {int(x) for x in sys.argv[sys.argv.index('--ids') + 1].split(',')}
    fetch_ep = getattr(EH, 'fetch', None) or getattr(EH, 'get')
    n = 0
    global NOCAST
    NOCAST = GF._artist_nocast()
    nocast0 = len(NOCAST)
    for e in E:
        if e['id'] not in ids:
            continue
        us = [t.get('url') for t in e.get('tickets') or [] if t.get('url')] + [v for k, v in (e.get('links') or {}).items() if v and k != 'amazon']
        pia = next((u for u in us if 't.pia.jp' in u), None)
        ep = next((u for u in us if 'eplus.jp/sf/detail/' in u), None)
        arts, src = [], ''
        try:
            if pia:
                arts, src = BP.pia_cast(BP.fetch(pia)), 'ぴあ'
            elif ep:
                arts, src = EH.eplus_artists(fetch_ep(ep)), 'e+'
            else:
                src = 'ほかの売り場（組み立て側）'
        except Exception as ex:
            src = f'読めず {str(ex)[:40]}'
        time.sleep(1.0)
        new = '／'.join(arts)
        if arts:   # 🆕10/27 売り場の出演者の欄で確かめた印（アーティスト一覧の番人が「公演名＝名前」の組に求める）
            CHECKED[str(e['id'])] = {'cast': new, 'src': src, 'at': TODAY_S}
        if not arts and src in ('ぴあ', 'e+'):
            NOCAST[str(e['id'])] = f'{src} に出演者の記載なし（{TODAY_S} 確認）'
        if new and new != e.get('artist'):
            print(f"id{e['id']} [{src}] {(e.get('artist') or '')[:40]} → {new[:60]}")
            n += 1
            if apply:
                e['artist'] = new
        else:
            print(f"id{e['id']} [{src}] そのまま（出演が読めない）: {(e.get('artist') or '')[:40]}")
    print(f'refetch_artist: 直す {n} / 対象 {len(ids)} / 売り場に出演者の記載なし {len(NOCAST) - nocast0}' + (' → 書いた' if apply and n else ''))
    if apply:
        json.dump(NOCAST, io.open(ROOT + 'tools/artist_nocast.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        json.dump(CHECKED, io.open(CHECKED_F, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    if apply and n:
        # 🚨10/27 売り場を読んでいる間（数時間）にほかの道具が index.html に書く＝最初に読んだ写しを書き戻すとその分が消える
        #   （livePocket の投入486件を上書きしかけた）→ 書く直前に読み直して、出演者の欄だけ id で差し替える
        #   --lock <ファイル>＝その間だけほかの道具と順番を取る（無ければ作って、書いたら消す）
        lock = sys.argv[sys.argv.index('--lock') + 1] if '--lock' in sys.argv else None
        while lock:
            try:
                fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'refetch_artist'); os.close(fd); break
            except FileExistsError:
                time.sleep(5)
        try:
            new_art = {e['id']: e.get('artist') for e in E if e['id'] in ids}
            s = io.open(ROOT + 'index.html', encoding='utf-8', newline='').read()
            mm = re.search(r'const\s+EVENTS\s*=\s*(\[)', s)
            st = mm.start(1)
            E2, end = json.JSONDecoder().raw_decode(s, st)
            for e in E2:
                if e['id'] in new_art:
                    e['artist'] = new_art[e['id']]
            body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E2) + '\n]'
            s = s[:st] + body.replace('\n', '\r\n') + s[end:]
            io.open(ROOT + 'index.html', 'wb').write(s.encode('utf-8'))
        finally:
            if lock:
                os.remove(lock)


if __name__ == '__main__':
    main()
