# -*- coding: utf-8 -*-
"""8/9 ヒール削除候補を e+ で裏取り（ぴあ0枠は削除理由にならない）。
今日8/9発売の2件(130/2401)は別扱いなので除外。"""
import io
import subprocess
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

CANDS = [
    (1071, "ニコラ・テスラ(東京9/6-9/29 STALE疑い)", "ニコラ・テスラ"),
    (1644, "BONNIE PINK 東京9/21", "BONNIE PINK"),
    (1656, "Summer Eye 東京・愛知10/4-10/8", "Summer Eye"),
    (2223, "宝塚星組 RRR 兵庫9/26・9/30", "RRR×TAKA"),
    (2340, "osage 宮城10/4", "osage"),
    (2341, "GANG PARADE 広島9/5", "GANG PARADE"),
    (2415, "鶴瓶×サンドウィッチマン 東京9/13", "笑福亭鶴瓶"),
    (2416, "白酒・一之輔 大手町二人会 東京9/14", "一之輔"),
    (3137, "壷阪健登 東京8/28", "壷阪健登"),
    (3287, "パンキッシュガーデン 東京9/2", "パンキッシュガーデン"),
    (3392, "ミキティダイニング 東京8/15", "ミキティダイニング"),
    (3432, "セントラル愛知交響楽団 愛知10/3", "セントラル愛知交響楽団"),
    (3513, "大相撲九月場所 東京9/13-9/27", "大相撲九月場所"),
    (3670, "仮面ライダーゼッツ 東京8/11", "仮面ライダーゼッツ"),
    (3872, "PM AGENCY 40th 沖縄11/14", "PM AGENCY"),
    (3875, "タイムトラベラーズ・ワイフ 東京9/5-・大阪10/2-", "タイムトラベラーズ・ワイフ"),
]

for i, (eid, name, kw) in enumerate(CANDS):
    if i:
        time.sleep(4)
    r = subprocess.run([sys.executable, "tmp/eplus_search2_0803.py", kw], capture_output=True)
    txt = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace").strip()
    lines = [ln for ln in txt.splitlines() if ln.strip() and not ln.startswith("len=")]
    print("=" * 78)
    print("id%d %s ／ e+検索語「%s」" % (eid, name, kw))
    if err:
        print("   [stderr] " + err.splitlines()[-1][:150])
    if not lines:
        print("   （ヒット無し）")
    for ln in lines[:12]:
        print("   " + ln)
