# -*- coding: utf-8 -*-
"""9/15夜のX投稿（9/16発売）に出したライブの取りこぼし総ざらい・2本め（読むだけ）。
1本め（audit_posts.py）で長すぎる・公演名っぽいとして外れた73件から、ツアーや別の日程を持っていそうな名前を
**短い呼び名**にして引く（手で選んだ）。主役の3組（ロッテ×日本ハム・新日本プロレス・ヨーヨー・マ）も入れる。
使い方: python tmp/x0916/audit_posts2.py
出力: tmp/x0916/audit_posts2.txt
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
    '千葉ロッテマリーンズ対北海道日本ハムファイターズ', 'ヨーヨー・マ', '野村萬斎', '前川清', '神韻', '世良公則', '渡辺美里',
    '東京都交響楽団', 'ワハハ本舗', '牛田智大', '角野隼斗', 'NDRエルプフィルハーモニー', '佐渡裕', 'シエナ・ウインド',
    '横山幸雄', '群馬交響楽団', '三遊亭白鳥', '三遊亭兼好', '春風亭一花', '田津原理音', 'コラアゲンはいごうまん',
    'ウィーン・ヨハン・シュトラウス', 'ウィーン・フォルクスオーパー', 'バッハ・コレギウム・ジャパン', '東京シティ・フィル',
    'セントラル愛知交響楽団', '日本フィルハーモニー交響楽団', '東京21世紀管弦楽団', '松居直美', '柏木広樹',
    '爆笑!!お笑いスーパーライブ', 'OSAKA COMEDY FESTIVAL', '近藤真彦', '青年団', '大槻能楽堂', '国立能楽堂',
    '松本山雅', 'サガン鳥栖', 'レイラック滋賀', '深堀隆介',
]
TODAY = datetime.date.today().isoformat()
evs = pma.load_events()
reg = pma.registered_cds(evs)
excl = pma.load_excluded()
print('引く名前 %d' % len(KWS))
pma.audit(KWS, reg, excl, 5, 'tmp/x0916/audit_state2.json', 'tmp/x0916/audit_posts2.txt', prior=None, rls_from=None, today=TODAY)
print('→ tmp/x0916/audit_posts2.txt')
