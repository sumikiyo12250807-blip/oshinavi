# -*- coding: utf-8 -*-
"""livePocket の「日付ごとに別ページ」の催しを1エントリに畳む（2026-09-28 夜）。

ユーザー「【北九州】9/29(火) 事前予約【アニメ「鬼滅の刃」…コラボレーションカフェ… これまとめられるよね？」
        「livePocketの日付別22組もまとめて」

  python tools/fold_livepocket_daily.py            … 下見（組と畳んだ後の名前・会期・枠数）
  python tools/fold_livepocket_daily.py --apply    … 書き換え
🚨毎回 inject_livepocket.py --apply の**後に**流す（新しく出た日が既存の組に入るので、同じ催しがまた分かれる）。

## 組の決め方
名前から日付（「10/24（土）」「10/24(土)」「10月24日」「10/24」）を抜き、空白と【】＜＞<>を落とした文字 ＋ 会場 が同じ。
- 1部／2部は名前が違う＝別の組のまま（開演時刻が違う別の回）。
- 登録済み（index.html）の livePocket 由来エントリどうしだけを畳む。

## 畳み方（[[feedback_longrun_event]]・[[feedback_tour_per_ticket_url]]・[[feedback_dedup_badges_keeps_urls]]）
- いちばん小さい id に全部の枠を集める。枠は**それぞれ自分のページのURLのまま**（売り場を消さない）＝枠の数は足し算で一致を確かめる
- name/artist＝最小idの名前から日付を抜いたもの
- date＝全ページの最終日／dateLabel＝全ページの本当の初日〜最終日（各ページの dateLabel に書いた日付を全部拾う）
- 畳まれた側の id は欠番（振り直さない）・NEW_ORDER からも抜く（[[feedback_new_list_order_lock]]）
- 🚨index.html の書式（EVENTS は indent=2・CRLF）を保つ＝1行に潰さない（2026-09-28 夜に一度潰した）
"""
import collections
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
DATE = re.compile(r'\d{1,2}/\d{1,2}\s*[（(][^)）]*[)）]|\d{1,2}月\d{1,2}日\s*[（(][^)）]*[)）]|\d{1,2}月\d{1,2}日|\d{1,2}/\d{1,2}')
WD = '月火水木金土日'


def key(e):
    return (re.sub(r'[\s【】＜＞<>]+', '', DATE.sub('', e['name'])), e.get('venue'))


def clean_name(n):
    n = DATE.sub('', n)
    n = re.sub(r'【\s*】|（\s*）|\(\s*\)|＜\s*＞|<\s*>', '', n)      # 日付だけ入っていたカッコ
    n = re.sub(r'【\s+', '【', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n


def label_dates(e):
    out = []
    for y, m, d in re.findall(r'(\d{4})年(\d{1,2})月(\d{1,2})日', e.get('dateLabel') or ''):
        out.append('%s-%02d-%02d' % (y, int(m), int(d)))
    # 「2026年10月24日(土)〜11月3日(火)」の後ろ側（年なし）
    m2 = re.search(r'(\d{4})年\d{1,2}月\d{1,2}日[^〜]*〜(\d{1,2})月(\d{1,2})日', e.get('dateLabel') or '')
    if m2:
        out.append('%s-%02d-%02d' % (m2.group(1), int(m2.group(2)), int(m2.group(3))))
    return out + [e['date']]


def jp(iso, with_year=True):
    dt = datetime.date.fromisoformat(iso)
    return ('%d年' % dt.year if with_year else '') + '%d月%d日(%s)' % (dt.month, dt.day, WD[dt.weekday()])


def main():
    apply = '--apply' in sys.argv
    P = 'index.html'
    s = io.open(P, encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', s, re.S)
    ev = json.loads(m.group(2))
    groups = collections.defaultdict(list)
    for e in ev:
        if (e.get('links') or {}).get('livepocket'):
            groups[key(e)].append(e)
    drop, nfold = set(), 0
    for k, g in groups.items():
        if len(g) < 2:
            continue
        g.sort(key=lambda e: e['id'])
        K = g[0]
        before = sum(len(e.get('tickets') or []) for e in g)
        ds = sorted(d for e in g for d in label_dates(e))
        first, last = ds[0], ds[-1]
        tks = []
        for e in sorted(g, key=lambda e: (min(label_dates(e)), e['id'])):
            tks += e.get('tickets') or []
        nm = clean_name(K['name'])
        print('■ %s件 → id%s ｜%s ｜%s' % (len(g), K['id'], nm[:60], K.get('venue')))
        print('    畳む id: %s' % ', '.join(str(e['id']) for e in g[1:]))
        lab = jp(first) if first == last else jp(first) + '〜' + jp(last, first[:4] != last[:4])
        print('    会期 %s ／ 枠 %d → %d' % (lab, before, len(tks)))
        assert before == len(tks)
        nfold += 1
        if apply:
            K['name'] = nm
            if K.get('artist') == g[0]['name'] or DATE.search(K.get('artist') or ''):
                K['artist'] = nm
            K['date'] = last
            K['dateLabel'] = lab
            K['tickets'] = tks
            drop |= {e['id'] for e in g[1:]}
    print('組 %d ／ 畳まれて欠番になる id %d件' % (nfold, len(drop) if apply else sum(len(g) - 1 for g in groups.values() if len(g) > 1)))
    if apply and drop:
        ev = [e for e in ev if e['id'] not in drop]
        s = s[:m.start(2)] + json.dumps(ev, ensure_ascii=False, indent=2).replace('\n', '\r\n') + s[m.end(2):]
        mo = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])', s)
        arr = [x for x in json.loads(mo.group(2)) if x not in drop]
        s = s[:mo.start(2)] + '[' + ', '.join(map(str, arr)) + ']' + s[mo.end(2):]
        io.open(P, 'w', encoding='utf-8', newline='').write(s)
        print('applied')


if __name__ == '__main__':
    main()
