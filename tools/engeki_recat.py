# -*- coding: utf-8 -*-
"""genre=engeki のエントリを、ぴあの実ページのカテゴリ(<title>末尾)で再分類する。

ユーザー指示 2026-08-13＝「ぴあがミュージカルって言ってる物だけミュージカルにして
後は伝統とかダンスとかぴあとかを参考にしたらいい」。

  python tools/engeki_recat.py            走査のみ → tmp/engeki_recat.json + 一覧
  python tools/engeki_recat.py --apply    走査結果を index.html に適用

・カテゴリ→ジャンルの対応は build_pia_entries.PIA_GENRE_MAP をそのまま使う（二重管理しない）
・取れた _piaSub は必ずエントリに残す（次回から人が推測しなくて済む）
・ぴあURLが無い/取れないものは「要目視」として触らない
・index.html は CRLF 維持（memory: feedback_index_html_crlf_preserve）
"""
import io, json, os, re, sys, time, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

from build_pia_entries import fetch, pia_subcat, genre_from_subcat, PIA_GENRE_MAP  # noqa
from check_expired import extract_events_array  # noqa

APPLY = '--apply' in sys.argv
OUT = 'tmp/engeki_recat.json'


def scan():
    ev = [e for e in extract_events_array('index.html')
          if e.get('verified') is True and e.get('genre') == 'engeki']
    rows = []
    for i, e in enumerate(ev, 1):
        url = (e.get('links') or {}).get('pia')
        rec = {'id': e['id'], 'name': e.get('name'), 'url': url,
               'cat': None, 'sub': None, 'new_genre': None, 'extra': None, 'note': ''}
        if not url:
            rec['note'] = 'ぴあURL無し→要目視'
            rows.append(rec)
            print('[%d/%d] %d ぴあURL無し' % (i, len(ev), e['id']))
            continue
        try:
            h = fetch(url)
            cs = pia_subcat(h)
        except Exception as ex:
            rec['note'] = 'fetch失敗: %s' % type(ex).__name__
            rows.append(rec)
            print('[%d/%d] %d %s' % (i, len(ev), e['id'], rec['note']))
            time.sleep(2.0)
            continue
        if not cs:
            rec['note'] = 'カテゴリ取れず(bundle等)→要目視'
        else:
            cat, sub = cs
            rec['cat'], rec['sub'] = cat, sub
            if sub in PIA_GENRE_MAP:
                g, extra = PIA_GENRE_MAP[sub]
                rec['new_genre'], rec['extra'] = g, extra
            else:
                rec['note'] = 'PIA_GENRE_MAP未収載: %s' % sub
        rows.append(rec)
        print('[%d/%d] %d %-22s → %s %s' % (
            i, len(ev), e['id'], (rec['sub'] or '-')[:22],
            rec['new_genre'] or '-', rec['note']))
        time.sleep(1.2)          # 429よけ
    json.dump(rows, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return rows


def apply(rows):
    h = io.open('index.html', encoding='utf-8', newline='').read()
    NL = '\r\n' if '\r\n' in h else '\n'
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    EVENTS = json.loads(m.group(2))
    by_id = {e['id']: e for e in EVENTS}
    n = 0
    for r in rows:
        e = by_id.get(r['id'])
        if not e or not r.get('sub'):
            continue
        e['_piaSub'] = r['sub']            # ぴあが何と言っていたかを必ず残す
        g = r.get('new_genre')
        if not g or g == e.get('genre'):
            continue
        e['genre'] = g
        if r.get('extra'):
            ex = [x for x in (e.get('extraGenres') or []) if x != g]
            if r['extra'] not in ex:
                ex.append(r['extra'])
            e['extraGenres'] = ex
        n += 1
    bak = 'index.html.bak_%s_engeki_recat' % datetime.date.today().strftime('%m%d')
    io.open(bak, 'w', encoding='utf-8', newline='').write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
    io.open('index.html', 'w', encoding='utf-8', newline='').write(
        h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print('=== ジャンル変更 %d件 / _piaSub 記録 %d件 (backup %s) ===' % (
        n, sum(1 for r in rows if r.get('sub')), bak))


if __name__ == '__main__':
    if APPLY and os.path.exists(OUT):
        rows = json.load(io.open(OUT, encoding='utf-8'))
    else:
        rows = scan()
    if APPLY:
        apply(rows)
    else:
        import collections
        c = collections.Counter(r.get('new_genre') or ('!' + (r.get('note') or '?')) for r in rows)
        print('\n=== 走査結果 %d件 ===' % len(rows))
        for k, v in c.most_common():
            print('  %-28s %3d' % (k, v))
        print('(適用は --apply)')
