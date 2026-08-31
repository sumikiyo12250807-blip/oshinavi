# -*- coding: utf-8 -*-
"""e+エントリの venue / dateLabel / prefecture を、枠(ticket)の実ページから作り直す。

なぜ要るか（2026-09-01 に見つけた欠け）:
  build は「JSON-LD が会場名を持っている行」だけを uniq_venues に積む。
  e+ の -P ページは会場名が空のことがあり、その公演は**会場一覧から落ちる**。
  結果、13県ぶんの枠を持つ黒蜜(5991)が「全国ツアー（柏616／HEAVEN'S ROCK宇都宮）」、
  5県ぶんの枠を持つヤミテラ(5993)が「京都MOJO」の単独公演に見えていた。
  dateLabel も同じ理由で期間が短く出る（10/1〜10/22 なのに実際は 12/19 まである）。

🚨 tickets には一切触らない。触ると枠が消える（refresh は枠を落とすことがある＝
   2026-09-01 のドライランで 5996 が 8→5、6009 が 20→14 になった）。
   ここで直すのは「見出しの表記」だけ。

使い方:
  python tools/fix_eplus_venue_label.py            # ドライラン（差分を出すだけ）
  python tools/fix_eplus_venue_label.py --apply
  python tools/fix_eplus_venue_label.py --ids 5991,5993 --apply
"""
import argparse
import datetime
import json
import re
import sys
import time

sys.path.insert(0, 'tools')
from eplus_harvest import fetch, parse_ld, jp_date, fix_half_kana  # noqa: E402

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

PATH = 'index.html'
PREF_ENUM_MAX = 4   # 〜4県は県名を列挙・5県以上は「全国」（ぴあ側と同じ規則・ユーザー確定2026-08-03）


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--ids', default='')
    args = ap.parse_args()
    only = {int(x) for x in args.ids.split(',') if x.strip()}

    # index.html は CRLF。newline='' で読み書きする（memory: feedback_index_html_crlf_preserve）
    src = open(PATH, encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    EVENTS = json.loads(m.group(2))

    cache = {}
    changed = []
    for e in EVENTS:
        if only:
            if e.get('id') not in only:
                continue
        elif e.get('genre') != 'new' or not (e.get('links') or {}).get('eplus'):
            continue

        urls = list(dict.fromkeys(
            [t.get('url') for t in e.get('tickets', []) if t.get('url')]
            or [(e.get('links') or {}).get('eplus')]))
        shows = {}          # (iso, venue) -> pref
        for u in urls:
            if not u or '/sf/detail/' not in u:
                continue
            if u not in cache:
                try:
                    cache[u] = fetch(u)
                except Exception as ex:
                    print(f'  !! id{e["id"]} {u} 取得失敗 {ex}')
                    cache[u] = ''
                time.sleep(0.4)
            for ev in parse_ld(cache[u]):
                if ev.get('date'):
                    shows[(ev['date'], ev.get('venue') or '')] = ev.get('pref') or ''
        if not shows:
            print(f'  △ id{e["id"]} {e.get("artist","")}: 実ページから公演を取れず → 触らない')
            continue

        venues = list(dict.fromkeys(v for (_d, v) in shows if v))
        prefs = list(dict.fromkeys(p for p in shows.values() if p))
        dates = sorted(d for (d, _v) in shows)
        d0, d1 = dates[0], dates[-1]

        # 🚨直すのは「会場が抜け落ちていた」型だけ＝**新しい会場一覧が古い一覧を丸ごと含む**時に限る。
        #   並び順が違うだけ／e+が会場名を改称しただけのエントリまで書き換えると、
        #   人が手で直した表記（6000「大阪・東京」・6004 の統合表記）を巻き戻してしまう。
        old_venues = set(re.findall(r'[^／（）]+', re.sub(r'^全国ツアー', '', e.get('venue') or '')))
        old_venues = {v.strip() for v in old_venues if v.strip()}
        if not (old_venues < set(venues)):
            continue

        if len(venues) <= 1:
            pref = prefs[0] if prefs else e.get('prefecture', '')
            venue = venues[0] if venues else e.get('venue', '')
            dlabel = (f'{jp_date(d0)} {pref} {venue}' if d0 == d1
                      else f'{jp_date(d0)}〜{jp_date(d1)} {pref} {venue}')
        else:
            pref = ('・'.join(prefs) if 2 <= len(prefs) <= PREF_ENUM_MAX
                    else (prefs[0] if len(prefs) == 1 else '全国'))
            venue = '全国ツアー（' + '／'.join(venues) + '）'
            dlabel = f'{jp_date(d0)}〜{jp_date(d1)} 全国ツアー'

        venue, dlabel = fix_half_kana(venue), fix_half_kana(dlabel)
        diff = {}
        for k, v in (('venue', venue), ('dateLabel', dlabel), ('prefecture', pref)):
            if (e.get(k) or '') != v:
                diff[k] = (e.get(k) or '', v)
        if not diff:
            continue
        changed.append((e['id'], e.get('artist', ''), diff, len(shows)))
        if args.apply:
            e['venue'], e['dateLabel'], e['prefecture'] = venue, dlabel, pref

    print(f'=== 会場/公演期間の表記を作り直す対象 {len(changed)}件 ===')
    for eid, artist, diff, nshow in changed:
        print(f'\nid{eid} {artist}（実ページの公演 {nshow}件）')
        for k, (old, new) in diff.items():
            print(f'  {k}:\n    旧 {old}\n    新 {new}')

    if args.apply and changed:
        # index.html は CRLF。json.dumps は \n を吐くので元の改行に戻してから書く
        # （memory: feedback_index_html_crlf_preserve・戻し忘れると sort_guard が誤ブロックする）
        NL = '\r\n' if '\r\n' in src else '\n'
        bak = f'index.html.bak_{datetime.date.today():%m%d}_epvenue'
        open(bak, 'w', encoding='utf-8', newline='').write(src)
        body = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
        with open(PATH, 'w', encoding='utf-8', newline='') as f:
            f.write(src[:m.start()] + m.group(1) + body + m.group(3) + src[m.end():])
        print(f'\n✅ {len(changed)}件を index.html に書き込んだ（ticketsは無変更・backup {bak}）')
    elif not args.apply:
        print('\n（ドライラン。書き込むなら --apply）')


if __name__ == '__main__':
    main()
