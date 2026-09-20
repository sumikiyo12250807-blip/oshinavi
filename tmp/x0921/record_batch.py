# -*- coding: utf-8 -*-
"""今朝の投入を .claude/state/last_batch.json に記録する（翌朝の再チェックで使う）。"""
import io, json, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
P = '.claude/state/last_batch.json'
d = json.load(io.open(P, encoding='utf-8'))

d['batches'].append({
    'date': '2026-09-21',
    'slot': 'morning-fany',
    'id_from': 17585,
    'id_to': 20344,
    'count': 2760,
    'source': '🆕FANYチケット（吉本興業 ticket.fany.lol）の初投入。入口＝/search/event_more?<クエリ>&offset=N がJSONで一覧を全部返す（2026-09-21に割った）。公演2,930件・枠7,791枠を引いて2,760件7,557枠。tools/fany_harvest.py → build_fany_entries.py → inject_fany.py',
    'assigned': False,
    'rechecked': False,
    'note': '売り状態の語彙は6つだけ＝先着発売中/抽選受付中（買える）・先着発売前/抽選受付前（発売前）・先着発売終了（soldout+saleEnded＝販売終了）・抽選受付終了（soldout+presaleEnded＝先行終了）。🚨「予定枚数終了」の文言が一覧に出ない＝完売を一覧で判定しない（楽天と同じ型）。🚨1公演＝1エントリにした＝なんばグランド花月「本公演１回目」は78公演で出演者が51通りに日替わり＝畳むと誰が出るか壊れる。同日同会場の複数公演（480組）はバッジに開演時刻。抜き打ち突合＝/event/detail/18981 で公演数3・券種3・受付期間・状態が一覧JSONと完全一致。番人 tools/gate_fany_slots.py を新設＝一致1554/食い違い7（締切が売り場ごとに1日ずれる型＝昼に枠ごとの売り場で直す）/リンクだけ51。入れなかった85件は「名前×公演日×会場が既存と一致」＝うち62件は既存に links.fany を足した（51件に付いた）。⛔ぴあ以外なので振り分けはユーザー確認後。',
})
d['batches'].append({
    'date': '2026-09-21',
    'slot': 'morning-pia',
    'id_from': 20345,
    'id_to': 20371,
    'count': 27,
    'source': 'ぴあ発売前スイープ lg=01〜07（総1,151件・未登録32件）→ build_pia_entries で27件75枠',
    'assigned': False,
    'rechecked': False,
    'note': 'skip3件＝券種が0で組めなかった（カマタマーレ讃岐×ツエーゲン金沢 2636729／カマタマーレ讃岐×ロアッソ熊本 2636728／筑後SAKEフェスタ2026 2628304）＝w.pia直販形式かページが立つ前の疑い＝明日以降に再度拾う。reconcile_pia --new＝OK29/MISSING0/DROP0/STALE0/FETCH0/QC0（照合できた枠73/77・skip4は同締切の枠が複数で対を確定できない分）。🚨投入時にidが仮番号91000台で入ったので、その場でバックアップに戻して20345〜20371に振り直した。',
})
json.dump(d, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('last_batch.json に2件記録した（総%d件）' % len(d['batches']))
