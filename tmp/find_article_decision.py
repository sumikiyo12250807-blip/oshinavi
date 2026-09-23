# 9/16〜9/19の会話記録から、ユーザーの発言で記事（特集・深掘り・主役・ピックアップ）に触れたものを時刻つきで出す
import glob, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
KEYS = ['特集', '深掘り', 'ピックアップ', '記事', '絞', 'フォロワー', 'ドラクエ', '主役']
d = r'C:\Users\user\.claude\projects\C--Users-user-oshinavi'
files = sorted(glob.glob(os.path.join(d, '*.jsonl')), key=os.path.getmtime)[-8:]
for f in files:
    for ln in open(f, encoding='utf-8', errors='replace'):
        try:
            o = json.loads(ln)
        except Exception:
            continue
        if o.get('type') != 'user':
            continue
        ts = o.get('timestamp', '')
        if not ('2026-09-16' <= ts[:10] <= '2026-09-19'):
            continue
        c = o.get('message', {}).get('content')
        if isinstance(c, list):
            c = ' '.join(x.get('text', '') for x in c if isinstance(x, dict) and x.get('type') == 'text')
        if not isinstance(c, str) or c.startswith('<') or 'tool_use_id' in c:
            continue
        if any(k in c for k in KEYS) and len(c) < 1500:
            print(ts[:16], os.path.basename(f)[:8], '|', c.replace('\n', ' ')[:400])
