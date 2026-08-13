# -*- coding: utf-8 -*-
"""engeki_recat.py で「カテゴリ取れず(bundle等)」になった分を、bundleページの中の
個別公演ページ(event.do?eventCd=...)を1本開いてカテゴリを取り直す。

  python tools/engeki_recat_bundle.py           走査のみ → tmp/engeki_recat_bundle.json
  python tools/engeki_recat_bundle.py --apply   適用

bundleページ自体の<title>にはカテゴリが載らないが、子の個別ページには載る。
"""
import io, json, os, re, sys, time, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

from build_pia_entries import fetch, pia_subcat, PIA_GENRE_MAP  # noqa
from check_expired import extract_events_array  # noqa

APPLY = '--apply' in sys.argv
OUT = 'tmp/engeki_recat_bundle.json'
SRC = 'tmp/engeki_recat.json'


def child_event_url(h):
    """bundleページのHTMLから子の個別公演URLを1つ拾う。"""
    for m in re.finditer(r'event\.do\?eventCd=(\d+)', h or ''):
        return 'https://t.pia.jp/pia/event/event.do?eventCd=%s' % m.group(1)
    return None


def scan():
    prev = json.load(io.open(SRC, encoding='utf-8'))
    targets = [r for r in prev if not r.get('new_genre')
               and r.get('url') and 'カテゴリ取れず' in (r.get('note') or '')]
    rows = []
    for i, r in enumerate(targets, 1):
        rec = {'id': r['id'], 'name': r['name'], 'url': r['url'],
               'sub': None, 'new_genre': None, 'extra': None, 'note': ''}
        try:
            h = fetch(r['url'])
            cu = child_event_url(h)
            if not cu:
                rec['note'] = '子ページのリンクが無い→要目視'
            else:
                time.sleep(1.2)
                ch = fetch(cu)
                cs = pia_subcat(ch)
                if not cs:
                    rec['note'] = '子ページにもカテゴリ無し→要目視'
                else:
                    rec['sub'] = cs[1]
                    if cs[1] in PIA_GENRE_MAP:
                        rec['new_genre'], rec['extra'] = PIA_GENRE_MAP[cs[1]]
                    else:
                        rec['note'] = 'PIA_GENRE_MAP未収載: %s' % cs[1]
        except Exception as ex:
            rec['note'] = 'fetch失敗: %s' % type(ex).__name__
        rows.append(rec)
        print('[%d/%d] %d %-20s → %s %s' % (
            i, len(targets), rec['id'], (rec['sub'] or '-')[:20],
            rec['new_genre'] or '-', rec['note']))
        time.sleep(1.2)
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
        e['_piaSub'] = r['sub']
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
    bak = 'index.html.bak_%s_engeki_bundle' % datetime.date.today().strftime('%m%d')
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
        print('\n=== 走査 %d件 ===' % len(rows))
        for k, v in collections.Counter(
                r.get('new_genre') or ('!' + (r.get('note') or '?')) for r in rows).most_common():
            print('  %-30s %3d' % (k, v))
        print('(適用は --apply)')
