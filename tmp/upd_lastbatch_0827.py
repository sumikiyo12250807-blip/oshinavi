# -*- coding: utf-8 -*-
import json,io
p='.claude/state/last_batch.json'
d=json.load(io.open(p,encoding='utf-8'))
d['batches'].append({
 "date":"2026-08-27","slot":"morning","id_from":5332,"id_to":5431,"count":100,
 "source":"ぴあ 発売前 rlsStatus=0102(先着)＋0202(抽選) を7ジャンル総ざらい（🆕rlsIn=03をやめた初バッチ）",
 "assigned":False,"rechecked":False,
 "note":"🚨🎯**rlsIn=03は「30日以内に発売」の窓しか見ておらず、31日より先に発売される公演を一度も拾えていなかった**（8/27実測）。"
        "正しい絞り込みは rlsStatus=0102（先着・発売前）＋0202（抽選・受付前）＝発売前の実在庫は 1,383行→**1,694行**（+18%）。"
        "発売前はどのジャンルも1,000行未満なので sg×rg の分割は不要。詳細＝memory reference_pia_presale_full_filter。"
        "今日のスイープ＝ページ到達率100%（全14バケツ）／未掲載456件（URL単位）＝**31日より先に発売228件**・30日以内189件・発売日不明39件。"
        "うち同名既存156件（完全110/部分46）は統合行きに回し、候補261件から**発売が31日より先のものだけ100件**を投入（音楽41/クラシック29/演劇30）。"
        "投入前ゲート＝dupcheck_built 名前一致0・eventCd一致0／緩い部分一致0／build 100件とも成立(skip 0)／check_badges OK／check_order 違反0／CRLF bare-LF 0。"
        "🚨翌朝(8/28)に①独立再照合②**別エージェントの客観チェックを100件全部に**（8/26のユーザー決定）→振り分け。"
        "🚨統合待ちが156件たまっている（tmp/dup_0827.md）＝id72に7枠・id915に5枠・id2694に5枠など14件はツアーが分裂している疑い。"
})
io.open(p,'w',encoding='utf-8').write(json.dumps(d,ensure_ascii=False,indent=2))
print('ok', len(d['batches']))
