#!/bin/sh
# e+のジャンル一覧を順番に回す（e+は叩きすぎると503＝必ず直列）。
# 受付前（発売前ファースト）→ そのあと受付中。結果はジャンルごとに退避する。
cd /c/Users/user/oshinavi || exit 1
for g in j-pop rock-indies idol classic enka k-pop-asian anime-song hiphop-rap jazz-fusion visual voiceactor-live festival; do
  echo "########## $g 受付前 ##########"
  python -u tools/eplus_harvest.py presale "$g" 1 64 9999 受付前 2>&1 | grep -E "^(===|p64:|p1:)"
  cp tmp/eplus_presale.json "tmp/eplus_presale_${g}_0922.json" 2>/dev/null
  sleep 3
done
echo "ALL DONE"
