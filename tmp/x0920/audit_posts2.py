# -*- coding: utf-8 -*-
"""総ざらいの2本め（9/19夜）＝長い公演名で外れた63件を、短い呼び名で引き直す（tmp/x0914/audit_posts2.py の形）。
出力: tmp/x0920/audit_posts2.txt"""
import datetime, importlib.util, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
spec = importlib.util.spec_from_file_location('pma', os.path.join(ROOT, 'tools', 'pia_missing_audit.py'))
pma = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0]]
spec.loader.exec_module(pma)
TODAY = datetime.date.today().isoformat()
evs = pma.load_events()
reg = pma.registered_cds(evs)
excl = pma.load_excluded()
KWS = ['ALICE', '星影の人', '反田恭平', 'ぎふアジア映画祭', 'ルノワール', '鼓童', 'コーラスライン', 'プロジェクトセカイ',
       'スーパースターたちによる新春', 'レプタイルズショー', 'ヤング・プラハ', '田辺いちか', 'さまチャン', 'おしゃべりコンサート',
       '新喜劇出前ツアー', 'ツワモノたちの記憶', 'NDRエルプフィル', 'ゴッデス・オブ・スターダム', 'アルビレックス新潟レディース',
       'Meychan', '赤毛のアン', '新春歌謡フェスティバル', 'HEAVY METAL SOUNDHOUSE', 'ONE ASIA WORLD', 'イルカ',
       'エスポラーダ北海道', 'サガン鳥栖', '東京ヤクルトスワローズ', 'GASOLINE', '森川智之', '入船亭扇七', '新日本プロレス',
       'NADESHIKO', '小林研一郎', 'KID BANG', 'これぱ', 'X-OVER', 'ガトーショコラは半分こ', 'くーあい', '黎明の空',
       '擬人化にゃんた', '狂想ドッペル', '高田漣', 'Osaka Shion Wind Orchestra', 'MEME', 'IMPACT26', 'きばやし']
print('引く名前 %d' % len(KWS))
pma.audit(KWS, reg, excl, 5, 'tmp/x0920/audit_state2.json', 'tmp/x0920/audit_posts2.txt', prior=None, rls_from=None, today=TODAY)
print('-> tmp/x0920/audit_posts2.txt')
