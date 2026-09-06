# -*- coding: utf-8 -*-
"""あたしの削除候補とエージェントの独立結論を突合する。"""
import re

MINE = "16,268,271,302,411,498,631,732,759,938,1013,1061,1062,1116,1260,1288,1615,1616,1849,1920,1992,1993,1997,2008,2098,2178,2216,2226,2267,2279,2284,2288,2313,2353,2373,2504,2522,2624,2749,2806,2844,2918,3079,3271,3365,3441,3540,3632,3669,3711,3718,4017,4029,4145,4224,4270,4334,4346,4433,4737,4790,5081,5121,5321,5620,5633,6173,6182,6189,6264,6437,6710,6712,6952,6964"
# 上の75件 ＋ 公演終了済で soldout により見かけの生き枠だった10件
MINE_EXTRA = "2300,3120,3229,1613,2035,2341,4971,4980,4982,5239"

txt = open("tmp/agent_delcheck_0907.txt", encoding="utf-8").read()
m = re.search(r"--- \(A\) の id カンマ区切り ---\s*\n([0-9,\s]+)", txt)
agent = set(int(x) for x in m.group(1).replace("\n", "").split(",") if x.strip())

mine = set(int(x) for x in (MINE + "," + MINE_EXTRA).split(","))

with open("tmp/delcmp_0907.txt", "w", encoding="utf-8") as f:
    f.write("あたし %d件 / エージェント %d件\n\n" % (len(mine), len(agent)))
    f.write("一致 %d件\n" % len(mine & agent))
    f.write("あたしだけが消すと言った（=エージェントが止めた）: %s\n" % sorted(mine - agent))
    f.write("エージェントだけが消すと言った: %s\n" % sorted(agent - mine))
    f.write("\n最終の削除リスト（両方が一致したものだけ）:\n%s\n"
            % ",".join(str(x) for x in sorted(mine & agent)))
print("mine=%d agent=%d both=%d" % (len(mine), len(agent), len(mine & agent)))
