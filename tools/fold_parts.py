# -*- coding: utf-8 -*-
"""同じ日・同じ会場で「1部／2部」「昼の部／夜の部」だけ違う別カードを1件に畳む（2026-09-30 ユーザー決定）。

  python tools/fold_parts.py            … 下見（畳む組を出す）
  python tools/fold_parts.py --check    … 🔒ゲート＝畳み残しがあれば終了コード1（push前・投入後に回す）
  python tools/fold_parts.py --apply    … 畳む
  python tools/fold_parts.py --selftest

## 決まり
- ユーザー「ARSMAGNA Special Live ～月が舞う嵐の夜に～　これ１部２部まとめて」→「これもゲートに組み込んでよ」
- 組＝公演日・会場が同じで、名前から部の印（【1部】・第二部・(昼の部)・夜公演…）を外すと同じになるもの
- 畳む先＝いちばん小さい id。名前は部の印を外したもの、見出し（dateLabel）は畳む先のまま。
  枠は全部足す（各ページのURLのまま）。券種名が同じになる枠には部の印を頭に付けて見分ける。残りは欠番、NEW_ORDER からも外す
- ⛔**FANY は畳まない**＝1公演1エントリ（部ごとに出演者が変わる・[[reference_fany_ticket]]）
- ⛔**新着（genre:"new"）と振り分け済みが混ざる組は畳まない**＝ぴあ以外の振り分けはユーザー確認の後（報告だけ）
- 🆕同日ユーザー「あんまりいっぱいあるときは分けたほうがいいけど、少ないならまとめたほうが親切よね」
  ＝**3部までの組だけ畳む**（MAX_PARTS）。4部以上（青木マッチョ9部・オーディション4枠など）は別のまま
- 「1st／2nd」は部の印と見ない（オーディション1stステージ等と区別がつかない）
"""
import io
import json
import re
import sys
from collections import defaultdict

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

PART = re.compile(
    r'[\s　]*[【\[［（(〚《〈<\-－・]*[\s　]*'
    r'(?:第[1-9一二三四五六七八九]部|[1-9一二三四五六七八九]部|昼の部|夜の部|昼公演|夜公演)'
    r'[\s　]*(?:[（(][^）)]{0,6}[）)])?[\s　]*[】\]］）)〛》〉>\-－~〜～]*')


MAX_PARTS = 3   # 🆕2026-09-30 ユーザー「少ないならまとめたほうが親切」＝4部以上は分けたまま


def part_of(name):
    m = PART.search(name or '')
    return m.group(0).strip() if m else None


def base_of(name):
    return re.sub(r'[\s　]+', '', PART.sub('', name or ''))


LABEL_RE = re.compile(r'^【([^】]{1,12})】')


def bare_type(tp):
    """番人が比べる時に使う＝畳んだ時に付けた【1部】【昼の部】等の印を外す（両側に同じく当てる）。"""
    m = LABEL_RE.match(tp or '')
    if m and PART.search(m.group(1)) and PART.sub('', m.group(1)).strip() == '':
        return (tp or '')[m.end():]
    return tp


CORE = re.compile(r'第[1-9一二三四五六七八九]部|[1-9一二三四五六七八九]部|昼の部|夜の部|昼公演|夜公演')


def clean_label(p):
    """部の印の芯だけ（「夜公演（S席抽選販売）」→「夜公演」）。"""
    m = CORE.search(p or '')
    return m.group(0) if m else ''


def relabel(e):
    """_parts（飛び先→部）を持つエントリで、同じ券種名が並ぶ枠に部の印を付け直す（ヒールが外しても戻る）。
    返り値＝変えた枠の数。"""
    parts = e.get('_parts') or {}
    if not parts:
        return 0
    tks = e.get('tickets') or []
    bare = [bare_type(t.get('type')) for t in tks]
    n = 0
    for t, b in zip(tks, bare):
        lab = parts.get(t.get('url') or '')
        # 同じ名前が並ぶ時だけ印を付ける。並ばない時は触らない（売り場が自分で付けた【夜の部】を外さない＝25689 Rec●）
        new = '【%s】%s' % (lab, b) if (lab and bare.count(b) > 1) else t.get('type')
        if new != t.get('type'):
            t['type'] = new
            n += 1
    return n


def is_fany(e):
    if (e.get('links') or {}).get('fany'):
        return True
    return any('fany.lol' in (t.get('url') or '') for t in e.get('tickets') or [])


def groups(E):
    g = defaultdict(list)
    for e in E:
        if not part_of(e.get('name')) or is_fany(e):
            continue
        g[(base_of(e.get('name')), e.get('date'), (e.get('venue') or '').strip())].append(e)
    # 🆕2026-10-01 ユーザー「10/7 キャッツホール 1部 LH AT TA／2部 AT LH TA まとめて」＝部の印の後ろに出演順の略号が付き、
    #   印を外しても名前が揃わない型。1つ目の組に入らなかったものを「部の印より前の名前＋出演者（artist）＋日＋会場」でもう一度組む
    single = [v[0] for v in g.values() if len(v) == 1]
    g2 = defaultdict(list)
    for e in single:
        nm = e.get('name') or ''
        m = PART.search(nm)
        head = re.sub(r'[\s　]+', '', nm[:m.start()]) if m else ''
        art = (e.get('artist') or '').strip()
        if len(head) >= 2 and art:
            g2[(head, art, e.get('date'), (e.get('venue') or '').strip())].append(e)
    for k, v in g2.items():
        if len(v) >= 2:
            for e in v:
                g.pop((base_of(e.get('name')), e.get('date'), (e.get('venue') or '').strip()), None)
            g[('出演順違い',) + k] = v
    out, mixed = [], []
    for k, v in g.items():
        if len(v) < 2 or len(v) > MAX_PARTS:
            continue
        v = sorted(v, key=lambda e: e['id'])
        if len({e.get('genre') == 'new' for e in v}) > 1:
            mixed.append(v)
        else:
            out.append(v)
    return out, mixed


def fold(v):
    """v[0] へ畳む。返り値＝畳む先のエントリ（書き換え済み）"""
    head = v[0]
    tks, parts = [], dict(head.get('_parts') or {})
    for e in v:
        p = clean_label(part_of(e.get('name')))
        for t in e.get('tickets') or []:
            tks.append(dict(t))
            if p and t.get('url'):
                parts[t['url']] = p
        for u in (e.get('links') or {}).values():
            if p and u and isinstance(u, str) and u not in parts and 'amazon' not in u:
                parts[u] = p
    head['_parts'] = parts
    if len({base_of(e.get('name')) for e in v}) > 1:
        # 🆕2026-10-01 部ごとに副題・出演順が違う組（キャッツホール LH AT TA／AT LH TA・Shimotsuki見聞録 会議編／傍観編）
        #   ＝1部の副題を全体の名前にしない。部の印より前だけを名前にする
        nm = head.get('name') or ''
        mm = PART.search(nm)
        head['name'] = nm[:mm.start()].strip().rstrip(' 　〜～~-－・【(（[:：') if mm else nm
        if re.fullmatch(r'[\d/／.()（）月火水木金土日祝\s　]*', head['name'] or '') and head.get('artist'):
            # 部の印より前が日付だけ（「10/16(金)1部Pixy Sirius …」）＝出演者名を足す
            head['name'] = ('%s %s' % (head['name'], head['artist'])).strip()
    else:
        head['name'] = PART.sub('', head.get('name') or '').strip().rstrip(' 　〜～~-－・') or head.get('name')
    if (head.get('artist') or '') and part_of(head.get('artist')):
        head['artist'] = PART.sub('', head['artist']).strip() or head['artist']
    head['tickets'] = tks
    # 🆕2026-10-01 見出しの時刻が1部だけ（「10/7(水) 14:00」）にならないよう、部ごとの時刻を並べる（「14:00／18:00開演」）
    tms = []
    for e in v:
        for tm in re.findall(r'(\d{1,2}:\d{2})', e.get('dateLabel') or ''):
            if tm not in tms:
                tms.append(tm)
    if len(tms) > 1 and re.search(r'\d{1,2}:\d{2}', head.get('dateLabel') or ''):
        dl = head['dateLabel']
        i = re.search(r'\d{1,2}:\d{2}', dl).start()
        head['dateLabel'] = dl[:i] + '／'.join(sorted(tms, key=lambda s: tuple(map(int, s.split(':'))))) + '開演'
    relabel(head)
    for e in v[1:]:
        for k2, u in (e.get('links') or {}).items():
            if u and not (head.get('links') or {}).get(k2):
                head.setdefault('links', {})[k2] = u
    return head


def main():
    if '--selftest' in sys.argv:
        return _selftest()
    text = io.open('index.html', encoding='utf-8', newline='').read()
    m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
    st = m.start(1)
    E, end = json.JSONDecoder().raw_decode(text, st)
    out, mixed = groups(E)
    for v in out:
        print('畳む %s ← %s | %s %s' % (v[0]['id'], ','.join(str(e['id']) for e in v[1:]),
                                       v[0].get('date'), base_of(v[0].get('name'))[:40]))
    for v in mixed:
        print('⚠️畳まない（新着と振り分け済みが混ざる）%s | %s' % (','.join(str(e['id']) for e in v),
                                                         base_of(v[0].get('name'))[:40]))
    print('組 %d（畳まない %d）' % (len(out), len(mixed)))
    rl = sum(relabel(dict(e, tickets=[dict(t) for t in e.get('tickets') or []])) for e in E)
    print('印の付け直しが要る枠 %d（ヒールで外れた分）' % rl)
    if '--check' in sys.argv:
        return 1 if (out or rl) else 0
    if '--apply' not in sys.argv or not (out or rl):
        return 0
    drop = set()
    for v in out:
        fold(v)
        drop |= {e['id'] for e in v[1:]}
    for e in E:
        relabel(e)
    E = [e for e in E if e['id'] not in drop]
    crlf = '\r\n' in text[st:st + 2000]
    body = json.dumps(E, ensure_ascii=False, indent=2)
    if crlf:
        body = body.replace('\r\n', '\n').replace('\n', '\r\n')
    text = text[:st] + body + text[end:]
    mo = re.search(r'NEW_ORDER\s*=\s*\[([^\]]*)\]', text)
    if mo:
        ids = [x.strip() for x in mo.group(1).split(',') if x.strip() and int(x.strip()) not in drop]
        text = text[:mo.start(1)] + ','.join(ids) + text[mo.end(1):]
    data = text.encode('utf-8')
    if crlf and data.count(b'\r\n') != data.count(b'\n'):
        print('ABORT: CRLF が崩れる')
        return 2
    io.open('index.html', 'wb').write(data)
    print('畳んだ %d組・欠番 %d件' % (len(out), len(drop)))
    return 0


def _selftest():
    for n, b in [('【1部】ARSMAGNA Special Live ～月が舞う嵐の夜に～', 'ARSMAGNASpecialLive～月が舞う嵐の夜に～'),
                 ('EPIC 2部', 'EPIC'), ('CeroZ文化祭【第二部】', 'CeroZ文化祭'),
                 ('ALL MIND vol.08 1部(昼の部)', 'ALLMINDvol.08'),
                 ('『 じわっと侵食中 vol.5 (1部) 』( じわっときてる単独公演 )', '『じわっと侵食中vol.5』(じわっときてる単独公演)'),
                 ('〜BOCCHI Vol.39〜 夜の部', '〜BOCCHIVol.39〜'), ('X～第1部～', 'X～'), ('おどチャンテーマ別回2-1部-', 'おどチャンテーマ別回2')]:
        assert base_of(n) == b, (n, base_of(n))
    assert part_of('オーディション1stステージEAST') is None, '1st は部の印と見ない'
    assert part_of('青木マッチョ 初ファンイベント～第3部～')
    a = {'id': 1, 'name': '【1部】X', 'date': '2026-10-31', 'venue': 'V', 'genre': 'new', 'links': {'livepocket': 'a'},
         'tickets': [{'type': '一般（東京 10/31公演）', 'date': '2026-10-31', 'url': 'a'}]}
    b = {'id': 2, 'name': '【2部】X', 'date': '2026-10-31', 'venue': 'V', 'genre': 'new', 'links': {'livepocket': 'b'},
         'tickets': [{'type': '一般（東京 10/31公演）', 'date': '2026-10-31', 'url': 'b'}]}
    f = {'id': 3, 'name': 'Y 第一部', 'date': '2026-10-31', 'venue': 'W', 'links': {'fany': 'x'}, 'tickets': []}
    g = dict(f, id=4, name='Y 第二部')
    c = dict(b, id=5, genre='idol', date='2026-11-01')
    d = dict(a, id=6, date='2026-11-01')
    many = [dict(a, id=100 + i, name='Z 第%d部' % i, venue='M') for i in range(1, 5)]
    assert not groups(many)[0], '4部以上は畳まない'
    out, mixed = groups([a, b, f, g, c, d])
    assert [[e['id'] for e in v] for v in out] == [[1, 2]], out
    assert [[e['id'] for e in v] for v in mixed] == [[5, 6]], '新着と振り分け済みは畳まない'
    h = fold(out[0])
    assert h['name'] == 'X' and len(h['tickets']) == 2, h
    assert {t['type'] for t in h['tickets']} == {'【1部】一般（東京 10/31公演）', '【2部】一般（東京 10/31公演）'}, h['tickets']
    assert {t['url'] for t in h['tickets']} == {'a', 'b'}
    assert h['_parts'] == {'a': '1部', 'b': '2部'}, h['_parts']
    # ヒールが印を外しても付け直せる／番人は印を外して比べる
    for t in h['tickets']:
        t['type'] = bare_type(t['type'])
    assert relabel(h) == 2 and h['tickets'][0]['type'].startswith('【1部】')
    assert bare_type('【2部】一般（東京 10/31公演）') == '一般（東京 10/31公演）'
    assert bare_type('【FC先行】一般') == '【FC先行】一般', '部でない【】は外さない'
    assert bare_type('【昼の部】S席') == 'S席'
    assert clean_label(part_of('河合健太郎1st FAN MEETING 夜公演（S席抽選販売）')) == '夜公演'
    assert clean_label(part_of('ALL MIND vol.08 2部(夜の部)')) == '2部'
    print('selftest OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
