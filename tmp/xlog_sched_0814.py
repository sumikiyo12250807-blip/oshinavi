# -*- coding: utf-8 -*-
"""8/14に予約した9本を台帳に登録（計測はまだ＝数字はnull）。
予約時刻はXの予約一覧「Will send on ...」の実表示で照合済み。"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

P = 'tools/x_log.json'
d = json.load(open(P, encoding='utf-8'))
base = dict(posted="2026-08-14", measured=None, measured_h=None, imp=None, like=None,
            rt=None, reply=None, eng=None, detail_cl=None, profile=None, link_cl=None,
            link=True, tone="おねえ", source="claude_browser_schedule")
rows = [
    ("18:46", "イモトアヤコ すっぴんしゃん10周年イベント", "タレント(ラジオ系ファンイベント)", 1100000),
    ("19:01", "Uru", "J-POP(ソロ)", 183000),
    ("19:16", "MISIA", "J-POP(ソロ)", 140000),
    ("19:31", "スターダム 秋の4公演", "スポーツ(女子プロレス)", 100000),
    ("19:46", "サイダーガール", "ロック(バンド)", 68200),
    ("20:01", "雷獣チャンネル THE LIVE「PLAY」", "YouTuber", 67200),
    ("20:16", "おとぼけビ～バ～", "ロック(バンド)", 36200),
    ("20:31", "真空ジェシカのイベン父ちゃん・イベアンドトシ", "お笑い(単独)", 30000),
    ("20:46", "D'ERLANGER", "ロック(V系)", 13400),
]
add = []
for t, title, cat, fw in rows:
    r = dict(base)
    r.update(title=title, cat=cat, followers=fw, scheduled_at=t,
             note="8/14夜に15分おきで予約。フォロワー多い順で並べた（🚨この順位付けは8/2・8/14の実測で"
                  "外れている軸＝次回は『チケットを取りに行くファンダムか』で並べる）。本文にURLあり")
    add.append(r)
d['posts'].extend(add)
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('追加', len(add), '件 / 台帳合計', len(d['posts']))
for r in add:
    print('  %s %s' % (r['scheduled_at'], r['title'][:40]))
