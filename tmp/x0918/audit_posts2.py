# -*- coding: utf-8 -*-
"""9/17夜のX投稿に出したライブの取りこぼし総ざらい・2本め（読むだけ）。
1本め（audit_posts.py）は登録の artist 欄をそのままキーワードにしたので、公演名そのものが入っているエントリ
（「ディズニー・オン・クラシック ～まほうの夜の音楽会 2026」など66件）は長すぎる・公演名っぽいとして外れた。
ここでは、その中からツアーや別の日程を持っていそうな名前を**短い呼び名**にして引く（手で選んだ）。
使い方: python tmp/x0914/audit_posts2.py
出力: tmp/x0918/audit_posts2.txt
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

KWS = [  # 9/17夜＝1本めで長すぎて外れた名前の中から、ツアーや別日程を持っていそうなものを短い呼び名に
    'GENERATIONS', 'esq', 'Damian Hamada', 'My Little Lover', '三遊亭白鳥', '牛田智大', '角野隼斗', '世良公則',
    '桂文珍', 'シエナ・ウインド', 'ワハハ本舗', '大阪桐蔭高等学校吹奏楽部', 'コンドルズ', '田辺いちか', '落合博満',
    '山里亮太', 'ウィーン・フォルクスオーパー', 'バッハ・コレギウム・ジャパン', 'a flood of circle', '浜崎貴司',
    '橋村姫', 'シーナ&ロケッツ', 'ハリウッド・フェスティバル・オーケストラ', 'ビューティーこくぶ', '文学座',
    'コーラスライン', 'ファインディング・ネバーランド', '吉本新喜劇', 'ヨーヨー・マ', 'イルカ',
]
TODAY = datetime.date.today().isoformat()
evs = pma.load_events()
reg = pma.registered_cds(evs)
excl = pma.load_excluded()
print('引く名前 %d' % len(KWS))
pma.audit(KWS, reg, excl, 5, 'tmp/x0918/audit_state2.json', 'tmp/x0918/audit_posts2.txt', prior=None, rls_from=None, today=TODAY)
print('→ tmp/x0918/audit_posts2.txt')
