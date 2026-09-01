# -*- coding: utf-8 -*-
"""e+のビルド結果の artist 欄を、実ページの「出演」欄の出演者名で置き換える。

なぜ要るか（2026-09-01）:
  e+のライブハウス公演は、イベント名が**主催者名・箱の名前**になっている
  （「cubrick presents 二転三転 vol.110」「L主催」「株式会社DDユニット対バンライブ」）。
  ビルドは公演名からアーティスト名を作るので、そのまま入れると
  **推しの名前で探している人が見つけられない**（[[feedback_entry_template_standard]]）。
  実ページには <dt>出演</dt><dd>名前<br>名前…</dd> があるので、そこから連名を作る。

使い方:
  python tools/eplus_fill_performers.py tmp/eplus_built.json           # ドライラン
  python tools/eplus_fill_performers.py tmp/eplus_built.json --apply
"""
import html as H
import json
import re
import sys
import time

sys.path.insert(0, 'tools')
from eplus_harvest import fetch, fix_half_kana  # noqa: E402

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

MAXN = 5   # 連名は5組まで（それ以上は「ほか」）


def performers(html):
    m = re.search(r'<dt>\s*出演\s*</dt>\s*<dd>(.*?)</dd>', html, re.S)
    if not m:
        return []
    body = re.sub(r'<br\s*/?>', '\n', m.group(1))
    body = H.unescape(re.sub(r'<[^>]+>', '', body))
    # 出演者でない行（日付見出し・注記・「他」など）は落とす。残らなければ空を返して呼び元で元の名前を残す
    DROP = re.compile(
        r'^(?:$|※|and\s*more|以上|他$|ほか$|and\s*more…$|\(?敬称略\)?$|'
        r'day\s*\d+$|第[一二三四五六七八九十\d]+部$|昼の部$|夜の部$|'
        r'\d{1,2}\s*[月/]\s*\d{1,2}\s*[日)]?.*(?:出演|の部|\(.\))?$|'
        r'[-<【（(]?\s*(?:special\s*guest|guest\s*player|band\s*member|出演者|司会|ゲスト|'
        r'mc|o\.?a|オープニングアクト)\s*[->】）)]?[:：]?$)', re.I)

    out = []
    for ln in body.split('\n'):
        ln = re.sub(r'\s+', ' ', ln).strip(' 　/／、,')
        ln = re.sub(r'^[■●▲★☆◆・･・\-–—=＝\s]+', '', ln).strip()
        # 「【司会】徳光和夫」「<Band Member>」「ゲスト:原田波人」の見出し部分を外す
        ln = re.sub(r'^[【<＜]([^】>＞]{0,14})[】>＞]', '', ln).strip()
        ln = re.sub(r'^[^:：]{1,16}[:：]', '', ln).strip()
        ln = re.sub(r'^[■●▲★☆◆・･・\-–—]+', '', ln).strip(' 　/／、,')
        if not ln or len(ln) > 40 or DROP.match(ln):
            continue
        if ln in out:
            continue
        out.append(ln)
    return out


def main():
    src = sys.argv[1]
    apply = '--apply' in sys.argv
    entries = json.load(open(src, encoding='utf-8'))
    cache = {}
    changed = 0
    for e in entries:
        u = (e.get('links') or {}).get('eplus')
        if not u:
            continue
        if u not in cache:
            try:
                cache[u] = fetch(u)
            except Exception:
                cache[u] = ''
            time.sleep(0.35)
        ps = performers(cache[u])
        if not ps:
            continue
        name = '／'.join(ps[:MAXN]) + ('　ほか' if len(ps) > MAXN else '')
        name = fix_half_kana(name)
        if name == e.get('artist'):
            continue
        print('id%s\n  旧 %s\n  新 %s' % (e['id'], e.get('artist'), name))
        if apply:
            e['artist'] = name
        changed += 1
    print('\n出演者で置き換える %d件 / %d件中' % (changed, len(entries)))
    if apply:
        json.dump(entries, open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print('✅ %s に書き戻した' % src)
    else:
        print('（ドライラン。書き戻すなら --apply）')


if __name__ == '__main__':
    main()
