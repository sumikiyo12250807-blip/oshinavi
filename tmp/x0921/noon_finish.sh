#!/bin/sh
# 昼の便の締め＝書き込み系を**1本ずつ順番に**流す（index.htmlを同時に触らせない）。
# 使い方: sh tmp/x0921/noon_finish.sh
cd /c/Users/user/oshinavi || exit 1
set -e

echo "########## ① ZAIKOの番人（作り直しが当たったか全件突合）"
python -u tools/gate_zaiko_slots.py --src tmp/zaiko_0921f.json 2>&1 | tail -2

echo "########## ② TIGETの食い違い16件をヒール"
IDS=$(cat tmp/x0921/tiget_ng16.txt)
python -u tools/heal_tiget.py --ids "$IDS" --apply 2>&1 | tail -2

echo "########## ③ 昼の隠れ枠ヒールを当てる"
python -u tools/heal_stale_deadlines.py --apply 2>&1 | tail -3

echo "########## ④ 枠が本当に減った件だけ見る"
python -u tmp/x0921/heal_tiget_compare.py 2>&1 | tail -2

echo "########## ⑤ 本日発売の形（締切が入ったか）"
python -u tmp/x0921/today_sale_shape.py after 2>&1 | tail -1

echo "########## ⑥ ZAIKOの前後比較"
python -u tmp/x0921/zaiko_beforeafter.py 2>&1 | tail -1

echo "########## ⑦ 機械ゲート"
python -u tools/check_badges.py 2>&1 | tail -1
node tools/check_order.js 2>&1 | grep 違反
node tools/check_zero_badge.js 2>&1 | head -5 || true

echo "ALL DONE"
