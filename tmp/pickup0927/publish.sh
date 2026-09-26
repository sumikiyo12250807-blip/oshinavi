#!/bin/bash
# 9/27号の公開手順（ユーザーのOK後に実行）＝ページ一式を公開フォルダへ → トップのセクション差し替え → SSR → 詰め → 検査
set -e
cd /c/Users/user/oshinavi
python tmp/pickup0927/build_pages.py
mkdir -p pickup/2026-09-27
cp tmp/pickup0927/pages/*.html pickup/2026-09-27/
PYTHONIOENCODING=utf-8 python tools/apply_pickup.py tmp/pickup0927/section_top.html
PYTHONIOENCODING=utf-8 python tools/build_ai_page.py
PYTHONIOENCODING=utf-8 python tools/compact_events.py --apply
node tools/check_order.js | grep '並び順違反'
PYTHONIOENCODING=utf-8 python tools/check_badges.py | grep -E '^(OK|NG)'
grep -c 'pickup/2026-09-27/index.html' index.html
