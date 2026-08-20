# -*- coding: utf-8 -*-
import io, re

t = io.open(r"C:\Users\user\oshinavi\tmp\pia_check_out.txt", encoding="utf-8").read()
out = io.open(r"C:\Users\user\oshinavi\tmp\pia_slices.txt", "w", encoding="utf-8")
for blk in t.split("############ id=")[1:]:
    eid = blk.split("\n", 1)[0].strip()
    body = blk.split("---- TEXT ----", 1)[-1]
    m = re.search(r"公演エリア", body)
    s = m.start() if m else 0
    m2 = re.search(r"販売終了したチケット情報を表示|リセールチケット購入へ|メールで通知", body[s:])
    e = s + (m2.start() if m2 else 4000)
    seg = body[s:e]
    # drop the area-filter boilerplate
    seg = re.sub(r"公演エリア\n全国\n関東甲信越\n関西\n中部\n九州・沖縄\n北海道\n中国・四国\n東北\n北陸\n", "", seg)
    out.write("\n===== id=%s =====\n" % eid)
    out.write(seg.strip() + "\n")
out.close()
print("ok")
