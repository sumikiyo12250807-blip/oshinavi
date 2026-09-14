# -*- coding: utf-8 -*-
"""9/14夜のX投稿に出したライブの取りこぼし総ざらい・2本め（読むだけ）。
1本め（audit_posts.py）は登録の artist 欄をそのままキーワードにしたので、公演名そのものが入っているエントリ
（「ディズニー・オン・クラシック ～まほうの夜の音楽会 2026」など66件）は長すぎる・公演名っぽいとして外れた。
ここでは、その中からツアーや別の日程を持っていそうな名前を**短い呼び名**にして引く（手で選んだ）。
使い方: python tmp/x0914/audit_posts2.py
出力: tmp/x0914/audit_posts2.txt
"""
import datetime
import importlib.util
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.getcwd()
spec = importlib.util.spec_from_file_location('pma', os.path.join(ROOT, 'tools', 'pia_missing_audit.py'))
pma = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0]]
spec.loader.exec_module(pma)

KWS = [
    'ディズニー・オン・クラシック', 'ドラゴンクエスト', '東京フィルハーモニー', '野村萬斎', '吉本新喜劇', '酒井藍',
    '神韻', '一路真輝', '横山幸雄', '前川清', 'ヨーヨー・マ', 'オルケスタ・デ・ラ・ルス', '三遊亭小遊三', '林家たい平',
    '春風亭一花', '柏木広樹', '透明少女', '田津原理音', '三遊亭好太郎', 'バッハ・コレギウム・ジャパン',
    'ウィーン・フォルクスオーパー', '松居直美', 'セントラル愛知交響楽団', '東京都交響楽団', '日本フィルハーモニー',
    '群馬交響楽団', '神奈川フィルハーモニー', 'コラアゲンはいごうまん', '青年団', '浦和レッズレディース',
    '松本山雅', 'サガン鳥栖', '町田智子', '宝生会', '長唄吉住会',
]
TODAY = datetime.date.today().isoformat()
evs = pma.load_events()
reg = pma.registered_cds(evs)
excl = pma.load_excluded()
print('引く名前 %d' % len(KWS))
pma.audit(KWS, reg, excl, 5, 'tmp/x0914/audit_state2.json', 'tmp/x0914/audit_posts2.txt', prior=None, rls_from=None, today=TODAY)
print('→ tmp/x0914/audit_posts2.txt')
