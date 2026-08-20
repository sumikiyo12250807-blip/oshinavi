# -*- coding: utf-8 -*-
"""新しいMiniMaxキーが有効かを、課金の発生しない「照会」エンドポイントで確かめる。
動画生成(POST)はせず、存在しないtask_idをGETするだけ。
  ・キーが無効 → 認証エラー(invalid api key 等)
  ・キーが有効 → 「そんなtaskは無い」系のエラー = 認証は通っている
🚨キーそのものは絶対に出力しない。
"""
import json, os, sys, urllib.error, urllib.request

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

key = os.environ.get('MINIMAX_API_KEY', '').strip()
if not key:
    p = os.path.join(ROOT, '.minimax_key')
    key = open(p, encoding='utf-8').read().strip()
if not key:
    sys.exit('キーが読めない')

url = 'https://api.minimax.io/v2/query/video_generation/authcheck_dummy_task_id'
req = urllib.request.Request(url, method='GET')
req.add_header('Authorization', 'Bearer ' + key)
req.add_header('Content-Type', 'application/json')

try:
    with urllib.request.urlopen(req, timeout=60) as r:
        code, body = r.status, r.read().decode('utf-8', 'replace')
except urllib.error.HTTPError as e:
    code, body = e.code, e.read().decode('utf-8', 'replace')
except Exception as ex:
    print('通信エラー:', type(ex).__name__, str(ex)[:200]); raise SystemExit(1)

# 念のため、万が一にもキーが混ざっていたら伏せる
body = body.replace(key, '<KEY>')
print('HTTP', code)
try:
    j = json.loads(body)
    print(json.dumps(j, ensure_ascii=False)[:600])
except Exception:
    print(body[:600])
