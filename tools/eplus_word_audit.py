# -*- coding: utf-8 -*-
"""e+のアーティストページ（/sf/word/<id>）から**そのアーティストの公演を総ざらい**して、
index.html に載っているか／落ちているかを出す。

なぜ要るか（2026-09-01 ユーザー発見）:
  e+のハーベストは「ジャンル別の一覧（/sf/live/<genre>）」を頁送りして拾う。
  一覧はページ数に上限があるうえ、**対バン形式のライブは主催者名やイベント名で並ぶ**ので、
  出演するアーティストの名前では引っかからない。
  実例＝水上クリニックはアーティストページに9公演あるのに、うちは4公演しか拾えていなかった
  （水クリミニ単独診療／二転三転vol.110／RYO生誕祭／四季彩プラネタリウム／cultivate common values♯136 が抜け）。
  ぴあの [[feedback_pia_bundle_hides_shows]] と同じ型＝**一覧に出ない公演がある。名前で引くと出る**。

使い方:
  python tools/eplus_word_audit.py 0000168060 0000155195 ...
  python tools/eplus_word_audit.py --pool          # 新着プールのe+エントリを名前で総ざらい
  python tools/eplus_word_audit.py 0000168060 --json tmp/out.json   # 未登録分を候補JSONで出す
"""
import json
import re
import sys
import time

sys.path.insert(0, 'tools')
from eplus_harvest import fetch, parse_ld, parse_windows  # noqa: E402

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

TODAY = __import__('datetime').date.today()


def load_index():
    src = open('index.html', encoding='utf-8').read()
    ev = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', src, re.S).group(1))
    blob = {}
    for e in ev:
        blob[e['id']] = json.dumps(e, ensure_ascii=False)
    return ev, blob


def word_shows(word_id):
    """アーティストページ → [{eid,url,date,time,venue,pref,name,windows}]"""
    h = fetch('https://eplus.jp/sf/word/%s' % word_id)
    title = re.search(r'<title>(.*?)</title>', h, re.S)
    artist = re.sub(r'のチケット.*', '', title.group(1)).strip() if title else word_id
    urls = sorted(set('https://eplus.jp/sf/detail/' + u
                      for u in re.findall(r'/sf/detail/(\d{10}-P\d+P\d+)', h)))
    out = []
    for u in urls:
        try:
            hh = fetch(u)
        except Exception as ex:
            print('  !! %s 取得失敗 %s' % (u, ex))
            continue
        time.sleep(0.4)
        ld = parse_ld(hh)
        ws = [w for w in parse_windows(hh) if w['ed'] >= TODAY]
        if not ld:
            continue
        ev0 = ld[0]
        out.append({'eid': u.split('/sf/detail/')[1].split('-')[0], 'url': u,
                    'date': ev0.get('date'), 'time': ev0.get('time'),
                    'venue': ev0.get('venue'), 'pref': ev0.get('pref'),
                    'name': ev0.get('name'), 'nwin': len(ws),
                    'windows': [(w['label'], str(w['sd']), str(w['ed'])) for w in ws]})
    return artist, out


def main():
    argv = sys.argv[1:]
    outjson = None
    if '--json' in argv:
        i = argv.index('--json')
        outjson = argv[i + 1]
        del argv[i:i + 2]
    args = [a for a in argv if not a.startswith('--')]

    _ev, blob = load_index()
    allblob = '\n'.join(blob.values())

    if '--pool' in sys.argv:
        # 新着プールのe+エントリの実ページから /sf/word/ のidを集める
        seen, wids = set(), []
        targets = [e for e in _ev if e.get('genre') == 'new' and (e.get('links') or {}).get('eplus')]
        print('新着プールのe+エントリ %d件からアーティストページを集める…' % len(targets))
        for e in targets:
            u = (e.get('links') or {}).get('eplus')
            try:
                h = fetch(u)
            except Exception:
                continue
            time.sleep(0.3)
            for w in re.findall(r'/sf/word/(\d{10})', h):
                if w not in seen:
                    seen.add(w); wids.append(w)
        print('アーティストページ %d件' % len(wids))
        args = wids
    missing_all = []
    for wid in args:
        wid = re.sub(r'.*/sf/word/', '', wid).strip('/')
        artist, shows = word_shows(wid)
        miss = []
        print('\n=== %s（/sf/word/%s） 公演 %d件 ===' % (artist, wid, len(shows)))
        for s in shows:
            reg = s['eid'] in allblob
            mark = '✅登録' if reg else ('🚨未登録' if s['nwin'] else '  買える枠なし')
            print('  %s %s %s %s（%s）%s' % (
                mark, s['date'], s['time'] or '', s['venue'] or '', s['pref'] or '', (s['name'] or '')[:44]))
            for w in s['windows']:
                print('        枠 %s | 開始 %s | 締切 %s' % w)
            if not reg and s['nwin']:
                miss.append(s)
                print('        %s' % s['url'])
        print('  → 未登録で買える枠があるもの %d件 / %d件中' % (len(miss), len(shows)))
        missing_all += [dict(m, _artist=artist) for m in miss]

    if outjson and missing_all:
        json.dump(missing_all, open(outjson, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('\n未登録 %d件 → %s' % (len(missing_all), outjson))


if __name__ == '__main__':
    main()
