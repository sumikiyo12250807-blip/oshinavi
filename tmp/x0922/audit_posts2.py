# -*- coding: utf-8 -*-
"""9/21夜のX投稿に出したライブの取りこぼし総ざらい・2本め（読むだけ）。
1本め（audit_posts.py）は登録の artist 欄をそのままキーワードにしたので、公演名そのものが入っているエントリ
（「ディズニー・オン・クラシック ～まほうの夜の音楽会 2026」など66件）は長すぎる・公演名っぽいとして外れた。
ここでは、その中からツアーや別の日程を持っていそうな名前を**短い呼び名**にして引く（手で選んだ）。
使い方: python tmp/x0922/audit_posts2.py
出力: tmp/x0922/audit_posts2.txt
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

KWS = ['星影の人', '柳沢慎吾', 'でんじろう', '横山だいすけ', '特撰落語会', '高嶋ちさ子', '野村萬斎', 'ALICE', 'ファインディング・ネバーランド', '太川陽介', 'バブルガム・ブラザーズ', '大阪フィルハーモニー', '東京佼成ウインド', 'シエナ・ウインド', '朝日名人会', 'JIN JU HYUNG', '工藤静香', 'リポビタンD', 'レッドイーグルス', '春猿火', '理芽', '都響', 'AMUSEMENT EXPO', 'Sick2', 'ダンロップ女子オープン', 'MUZAジルベスター', '東京バッハバンド', '青春ブタ野郎', '帰還者の魔法']
TODAY = datetime.date.today().isoformat()
evs = pma.load_events()
reg = pma.registered_cds(evs)
excl = pma.load_excluded()
print('引く名前 %d' % len(KWS))
pma.audit(KWS, reg, excl, 5, 'tmp/x0922/audit_state2.json', 'tmp/x0922/audit_posts2.txt', prior=None, rls_from=None, today=TODAY)
print('→ tmp/x0922/audit_posts2.txt')
