# -*- coding: utf-8 -*-
"""8/13投稿2本の実測をx_log.jsonに記録（ユーザーのスクショ実測・推定値は入れない）。"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

P = 'tools/x_log.json'
d = json.load(open(P, encoding='utf-8'))
rows = [
    {"posted": "2026-08-13", "title": "2026 SEO EUNKWANG CONCERT [My Page] in TOKYO",
     "cat": "K-POP(ソロ/BTOB)", "measured": "2026-08-14", "measured_h": 20,
     "imp": 229, "like": 0, "rt": 0, "reply": 0, "eng": 13, "detail_cl": 4,
     "profile": 2, "link_cl": None, "link": True, "tone": "おねえ",
     "source": "claude_screenshot",
     "note": "エンゲージ率5.7%(13/229)＝台帳の1.3〜1.5%より明確に高い。❤/RT/返信は全部0なので13は全部クリック系。リンククリック欄はスクショ外(未取得)。翌8/14 12:00発売→当日中に予定枚数終了(id2815)"},
    {"posted": "2026-08-13", "title": "鋼の錬金術師×黄泉のツガイ展 札幌",
     "cat": "アニメ(展示)", "measured": "2026-08-14", "measured_h": 21,
     "imp": 627, "like": 0, "rt": 0, "reply": 0, "eng": 0, "detail_cl": 0,
     "profile": 0, "link_cl": 0, "link": True, "tone": "おねえ",
     "source": "claude_screenshot",
     "note": "🚨リーチは同日のK-POP投稿の2.7倍(627 vs 229)なのにエンゲージ0＝表示されただけで誰も動かなかった。エンゲージ0なので内訳(link_cl含む)も全部0で確定"},
]
d['posts'].extend(rows)
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('追加', len(rows), '件 / 台帳合計', len(d['posts']), '件')
for r in rows:
    print('  %s imp=%-4s eng=%-3s %s' % (r['posted'], r['imp'], r['eng'], r['title'][:40]))
