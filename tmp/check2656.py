#!/usr/bin/env python3
"""id=2656 KAWAII LAB. の登録枠とぴあ実枠を突き合わせ（枠数不一致1件の中身確認）"""
import io
import sys
import subprocess
sys.path.insert(0, 'tools')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from check_expired import extract_events_array

EVENTS = extract_events_array('index.html')
e = next(x for x in EVENTS if x.get('id') == 2656)
print('=== 登録内容 ===')
print('name:', e.get('name'))
print('venue:', e.get('venue'), '/ pref:', e.get('prefecture'), '/ 公演日:', e.get('date'))
print('dateLabel:', e.get('dateLabel'))
for t in e.get('tickets', []):
    print(f"  枠: {t.get('type')} | date={t.get('date')} | startDate={t.get('startDate')}")
print('pia:', (e.get('links') or {}).get('pia'))
