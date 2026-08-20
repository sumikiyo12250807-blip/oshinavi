# -*- coding: utf-8 -*-
"""8/7 朝の削除候補を e+ キーワード検索で裏取りする（ぴあ0枠＝削除理由にならない）。
memory: feedback_delete_nonpia_blindspot / reference_eplus_keyword_search
"""
import io
import re
import subprocess
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# (id, 登録名, e+検索キーワード, 公演日)
CANDS = [
    (185, "斉藤朱夏", "斉藤朱夏", "8/16"),
    (717, "Damian Hamada's Creatures", "デイミアン浜田", "8/15"),
    (750, "山内総一郎", "山内総一郎", "8/22"),
    (813, "時速36km", "時速36km", "8/15"),
    (925, "忘れらんねえよ", "忘れらんねえよ", "8/11"),
    (1094, "「まんが日本昔ばなし」劇場", "まんが日本昔ばなし", "8/9"),
    (1456, "KINASHI CLASSIC in SAPPORO", "KINASHI CLASSIC", "8/8"),
    (2232, "ミュージカル『ジョセフ…ドリームコート』", "ジョセフ", "8/9"),
    (2850, "第41回 なとり夏まつり 大花火大会", "なとり夏まつり", "8/8"),
    (2873, "ハロ!コン 2026", "ハロー!プロジェクト", "8/9"),
    (2988, "ふぉ〜ゆ〜", "ふぉ〜ゆ〜", "8/9"),
    (3482, "Hump Back", "Hump Back", "11/7"),
    (3781, "島田秀平とカイダンさん!", "島田秀平", "10/18"),
    (1148, "猪狩翔一／飯田瑞規", "猪狩翔一", "8/6終了"),
    (3065, "栄ミナミ音楽祭パートナーズライブ", "栄ミナミ音楽祭", "8/6終了"),
]

for i, (eid, name, kw, day) in enumerate(CANDS):
    if i:
        time.sleep(4)
    r = subprocess.run(
        [sys.executable, "tmp/eplus_search2_0803.py", kw],
        capture_output=True,
    )
    txt = r.stdout.decode("utf-8", "replace")
    lines = [ln for ln in txt.splitlines() if ln.strip() and not ln.startswith("len=")]
    print("=" * 78)
    print("id=%d %s（公演%s）  e+検索語「%s」" % (eid, name, day, kw))
    if not lines:
        print("   （出力なし・失敗の可能性）")
        print(txt[:300])
        continue
    for ln in lines:
        print("   " + ln)
