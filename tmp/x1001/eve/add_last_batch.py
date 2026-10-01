# -*- coding: utf-8 -*-
# 10/1夜の新着収集（ユーザー「新着集めてきて」）を last_batch.json に記録＝翌朝の再チェック用
import io, json
p = 'C:/Users/user/oshinavi/.claude/state/last_batch.json'
d = json.load(io.open(p, encoding='utf-8'))
d['batches'] += [
    {"date": "2026-10-01", "slot": "evening", "id_from": 27121, "id_to": 27157, "count": 37, "source": "ZAIKO tmp/x1001/eve/zaiko_eve.json", "assigned": False, "rechecked": True, "note": "番人 36一致・27146は登録側に県名「大阪」があるだけの違い"},
    {"date": "2026-10-01", "slot": "evening", "id_from": 27158, "id_to": 27267, "count": 110, "source": "TIGET tmp/x1001/eve/tiget_eve.json（--stop-known 1）", "assigned": False, "rechecked": True, "note": "番人 110/110一致"},
    {"date": "2026-10-01", "slot": "evening", "id_from": 27268, "id_to": 27328, "count": 61, "source": "ぴあ発売前スイープ tmp/x1001/eve/presale_*", "assigned": False, "rechecked": True, "note": "reconcile_pia 61/61一致・既存13件に足し込み（消えた枠0）"},
    {"date": "2026-10-01", "slot": "evening", "id_from": 27329, "id_to": 27334, "count": 6, "source": "FANY tmp/x1001/eve/fany_eve.json", "assigned": False, "rechecked": True, "note": "heal_fany 41件→番人 一致1697・食い違い1（20428は今日の公演）"},
    {"date": "2026-10-01", "slot": "evening", "id_from": 27335, "id_to": 27596, "count": 262, "source": "livePocket tmp/x1001/eve/livepocket_eve.json（--pages 40）", "assigned": False, "rechecked": True, "note": "独立ゲート 275一致（19件は食い違いで入れない＝tmp/x1001/eve/lp_ng.txt）・13件は名前×日付が既存と一致で入れない・日別11組＋部違い8組を畳んだ"},
]
json.dump(d, io.open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(d['batches']))
