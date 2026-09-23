#!/bin/sh
# ぴあの発売前を全ジャンル回す（02演劇 03スポーツ 04映画 05アート 06イベント 07クラシック）。
# 01音楽は先に回した。ぴあは叩きすぎると429なので直列＋間を置く。
cd /c/Users/user/oshinavi || exit 1
for lg in 01 02 03 04 05 06 07; do
  echo "########## lg=$lg 発売前 ##########"
  python -u tools/presale_harvest.py "$lg" "tmp/x0922/presale_${lg}.json" 2>&1 | tail -3
  sleep 8
done
echo "ALL DONE"
