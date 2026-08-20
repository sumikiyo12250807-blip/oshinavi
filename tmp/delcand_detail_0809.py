# -*- coding: utf-8 -*-
"""削除候補のうち e+ で「生きて見えた」ものを個別ページで裏取り。
一覧の「一般発売」は券種名であって販売中とは限らない（feedback_delete_nonpia_blindspot）。"""
import io
import subprocess
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TARGETS = [
    (1071, "ニコラ・テスラ 紀伊國屋(東京) 受付〜9/10 18:00の枠",
     "https://eplus.jp/sf/detail/4543980001-P0030002P021027"),
    (1644, "BONNIE PINK Zepp DiverCity 受付〜9/17 18:00",
     "https://eplus.jp/sf/detail/0034210001-P0030185P021001"),
    (1656, "Summer Eye 24PILLARS(愛知) 一般〜10/3 23:59",
     "https://eplus.jp/sf/detail/3963800001-P0030011P021001"),
    (1656, "Summer Eye 京都磔磔 一般〜10/2 23:59",
     "https://eplus.jp/sf/detail/3963800001-P0030010P021001"),
    (2340, "osage 仙台enn3rd ★一般発売〜10/3 23:59",
     "https://eplus.jp/sf/detail/3030470001-P0030088P021001"),
    (2341, "GANG PARADE 広島LIVE VANQUISH 一般〜9/4 18:00",
     "https://eplus.jp/sf/detail/1975960001-P0030054P021001"),
    (3875, "タイムトラベラーズ・ワイフ EXシアター有明 ☆★一般発売〜8/23 18:00",
     "https://eplus.jp/sf/detail/4559520001-P0030002P021020"),
    (2415, "鶴瓶? ニッショーホール(東京) 一般〜9/10 18:00 ※公演同定要",
     "https://eplus.jp/sf/detail/4578660002-P0030001P021001"),
    (2223, "宝塚RRR e+貸切公演 特別プレ〜8/12 18:00",
     "https://eplus.jp/sf/detail/0015890190-P0030490P021001"),
]

for i, (eid, name, url) in enumerate(TARGETS):
    if i:
        time.sleep(4)
    print("=" * 78)
    print("id%d %s" % (eid, name))
    print("   " + url)
    r = subprocess.run([sys.executable, "tmp/eplus_detail_0803.py", url], capture_output=True)
    txt = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace").strip()
    if err:
        print("   [stderr] " + err.splitlines()[-1][:160])
    for ln in txt.splitlines():
        if ln.startswith("len="):
            continue
        print("   " + ln)
