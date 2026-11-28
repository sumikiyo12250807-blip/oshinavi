# -*- coding: utf-8 -*-
"""FANY のライブビューイングを1枚に畳む（2026-11-28 すちこ「M1グランプリ２０２６決勝ってやつ　ひとつにまとめられるのだよ　数増えててもこれじゃあ」）。

なぜ：build_fany_entries は「1公演＝1エントリ」（event_id・公演日・会場ごと）で組む。
  ライブビューイングは同じ公演を全国の映画館で流すので、映画館の数だけカードができる
  （M-1グランプリ2026＜準決勝＞ライブビューイング＝98枚・FANY event/detail/23700）。
畳み方：公演名に「ライブビューイング」があり、links.fany（event/detail）と公演日が同じエントリを1枚に。
  - いちばん小さい id を残す。tickets は全部そのまま残す（映画館ごとの申込URL /reception/…/<公演id> ＝
    inject_fany の重複の見方・heal_fany・gate_fany_slots・fany_mark_soldout が公演id で動くので消さない）
  - venue＝「全国の映画館 N館（最初の館 ほか）」・prefecture＝県を並べる・_lvFold＝畳んだ枚数
  - 消した id は NEW_ORDER からも外す
使い方：python tools/fold_fany_lv.py（下見）／--apply（鍵 tmp/x1112/index.lock の中で書く）
"""
import io, json, os, re, sys, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(R, 'index.html')
LK = os.path.join(R, 'tmp', 'x1112', 'index.lock')
PREF_ORDER = ['北海道', '青森', '岩手', '宮城', '秋田', '山形', '福島', '茨城', '栃木', '群馬', '埼玉', '千葉', '東京', '神奈川', '新潟', '富山', '石川', '福井',
              '山梨', '長野', '岐阜', '静岡', '愛知', '三重', '滋賀', '京都', '大阪', '兵庫', '奈良', '和歌山', '鳥取', '島根', '岡山', '広島', '山口', '徳島', '香川',
              '愛媛', '高知', '福岡', '佐賀', '長崎', '熊本', '大分', '宮崎', '鹿児島', '沖縄']


def pref_key(p):
    return PREF_ORDER.index(p) if p in PREF_ORDER else 99


def plan(E):
    g = collections.defaultdict(list)
    for e in E:
        nm = e.get('name') or ''
        fany = (e.get('links') or {}).get('fany') or ''
        if 'ライブビューイング' in nm and 'event/detail' in fany:
            g[(fany, e.get('date'), nm.split('@')[0].strip())].append(e)
    return {k: sorted(v, key=lambda e: e['id']) for k, v in g.items() if len(v) > 1}


def fold(group):
    keep = dict(group[0])
    venues, prefs, tickets = [], [], []
    for e in group:
        v = e.get('venue') or ''
        if v and v not in venues:
            venues.append(v)
        for p in (e.get('prefecture') or '').split('・'):
            if p and p not in prefs:
                prefs.append(p)
        for t in e.get('tickets') or []:
            tickets.append(t)
    prefs.sort(key=pref_key)
    tickets.sort(key=lambda t: (pref_key(re.findall(r'（([^（）\s]+) ', t.get('type') or '')[-1] if re.findall(r'（([^（）\s]+) ', t.get('type') or '') else ''), t.get('date') or ''))
    keep['venue'] = '全国の映画館 %d館（%s ほか）' % (len(venues), venues[0]) if len(venues) > 1 else venues[0]
    keep['prefecture'] = '・'.join(prefs)
    keep['tickets'] = tickets
    keep['_lvFold'] = len(group)
    return keep


def main():
    apply = '--apply' in sys.argv
    import compact_events as C
    if apply:
        while True:
            try:
                fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'fold_fany_lv'); os.close(fd); break
            except FileExistsError:
                time.sleep(10)
    try:
        src = io.open(IDX, encoding='utf-8', newline='').read()
        E = C.load(src)
        P = plan(E)
        drop, repl = set(), {}
        for k, grp in P.items():
            f = fold(grp)
            repl[f['id']] = f
            drop |= {e['id'] for e in grp[1:]}
            print('畳む %s ｜%d枚 → id%d ｜%s ｜枠 %d' % (k[2], len(grp), f['id'], f['venue'][:40], len(f['tickets'])))
        if not P:
            print('畳むものなし'); return 0
        before = {t.get('url') for e in E for t in e.get('tickets') or []}
        E2 = [repl.get(e['id'], e) for e in E if e['id'] not in drop]
        after = {t.get('url') for e in E2 for t in e.get('tickets') or []}
        assert before == after, ('枠の申込URLが消える', len(before - after))
        print('カード %d → %d（-%d）・枠の申込URL 消えた %d' % (len(E), len(E2), len(drop), len(before - after)))
        if apply:
            a, b, _ = C.locate(src)
            body = C.dump(E2, C.is_compact(src), '\r\n')
            s2 = src[:a] + body + src[b:]
            mo = re.search(r'NEW_ORDER\s*=\s*\[([^\]]*)\]', s2)
            ids = [y.strip() for y in mo.group(1).split(',') if y.strip() and int(y.strip()) not in drop]
            s2 = s2[:mo.start(1)] + ','.join(ids) + s2[mo.end(1):]
            assert s2.count('\r\r\n') == 0
            io.open(IDX, 'w', encoding='utf-8', newline='').write(s2)
            print('書いた')
    finally:
        if apply:
            os.remove(LK)
    return 0


if __name__ == '__main__':
    sys.exit(main())
