# -*- coding: utf-8 -*-
"""アーティスト一覧（artists.html）の番人（2026-10-27 新設・すちこ「確実じゃなきゃ載せるべきじゃない　もし載せるなら、完璧なゲートをちゃんと作らなきゃ」→「A」）。

  python tools/gate_artist_pages.py      … exit 0＝健全／1＝要対応（push しない）

見ること（一覧に出ている名前1つずつ・作品名『』のページは除く）:
  P 名前の元になったエントリが1件も無い（今の index.html から作り直すと出ない名前が一覧に残っている）
  Q 元のエントリの出演者の欄が公演名のまま（gate_fields M）か、売り場に出演者の記載が無い（artist_nocast）
  R ジャンルの名前（お笑い・J-POP…）・総称・告知文（SKIP_NAME）が名前になっている
  S 名前が公演名そのもの（元のエントリの name と同じ）で、しかもその名前の出演者がほかのどのエントリにも無い
     （例外＝tools/artist_ok.txt に人が書いた名前・グループ名と公演名が同じもの「サーカス」）
"""
import html
import io
import json
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import date

sys.path.insert(0, 'tools')
import build_artist_pages as B  # noqa: E402
import build_ai_page as A       # noqa: E402
import gate_fields as GF        # noqa: E402


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    today = date.today()
    events = [e for e in A.extract_events_array('index.html') if e.get('verified') is True and e.get('genre') != 'new']
    ok = GF._artist_ok()
    src = defaultdict(list)          # 名前 → 元のエントリ（買える枠があるもの）
    cast_names = set()               # 出演者の欄が売り場の出演者から来ている名前（全エントリ）
    for ev in events:
        if B.cast_ok(ev):
            for nm in B.artist_names(ev):
                cast_names.add(B.norm(nm))
        if not B.ticket_rows(ev, today):
            continue
        for nm in B.artist_names(ev):
            src[B.norm(nm)].append(ev)
    a = io.open('artists.html', encoding='utf-8').read()
    listed = [html.unescape(x) for x in re.findall(r'<li><a href="[^"]+">([^<]+)</a>', a)]
    P, Q, R, S = [], [], [], []
    for nm in listed:
        if nm.startswith('『') or nm.startswith('ミュージカル『'):
            continue
        k = B.norm(nm)
        evs = src.get(k, [])
        if not evs:
            P.append(nm); continue
        good = [e for e in evs if B.cast_ok(e)]
        if not good:
            Q.append((nm, evs[0]['id'], evs[0].get('artist')))
        if nm.lower() in B.GENRE_WORDS and not any(nm == (e.get('name') or '').strip() for e in evs):
            R.append(nm)
        elif B.SKIP_NAME.search(nm):
            R.append(nm)
        # 元のエントリが全部「公演名＝名前」＝ほかに出演者として出てくる公演が1つも無い時だけ鳴らす
        #   （YONA YONA WEEKENDERS のように別の公演でも出演者の名前として出ていれば本当の名前）
        t = unicodedata.normalize('NFKC', nm).strip()
        if (good and all(unicodedata.normalize('NFKC', (e.get('name') or '')).strip() == t for e in good)
                and len(t) >= 12 and nm not in ok and ' ' in t):
            S.append((nm, good[0]['id']))
    print(f'=== gate_artist_pages (today={today}) 一覧 {len(listed)}組 ===')
    for tag, xs in (('P 元のエントリが無い', P), ('Q 出演者の欄が公演名のまま／記載なし', Q), ('R ジャンル名・総称・告知文', R),
                    ('S 公演名そのもの（長い・空白入り）', S)):
        for x in xs[:30]:
            print(f'  {tag[0]} {x}')
    print(f'=== 集計: P {len(P)} / Q {len(Q)} / R {len(R)} / S {len(S)} ===')
    sys.exit(1 if (P or Q or R or S) else 0)


if __name__ == '__main__':
    main()
