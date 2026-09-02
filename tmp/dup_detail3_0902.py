# -*- coding: utf-8 -*-
"""dup_detail2の生テキストから、判定に効く欄だけ抜き出す。"""
import io, re
src = io.open('tmp/dup_detail2_0902.txt', encoding='utf-8').read()
o = io.open('tmp/dup_key_0902.txt', 'w', encoding='utf-8')
for blk in src.split('#####')[1:]:
    head = blk.split('\n')[0].strip()
    t = blk
    def grab(pat):
        m = re.search(pat, t)
        return m.group(1).strip() if m else ''
    o.write(u'### %s\n' % head)
    o.write(u'  出演タグ  : %s\n' % grab(r'@出演タグ: (.*)'))
    o.write(u'  公演期間  : %s\n' % grab(r'公演期間 (.*?) 会場'))
    o.write(u'  会場      : %s\n' % grab(r'会場 (.*?) (?:出演者など|注意事項|公演などに関する)'))
    o.write(u'  出演者など: %s\n' % grab(r'出演者など (.*?) (?:注意事項|公演などに関する)')[:300])
    o.write(u'  問合せ先  : %s\n' % grab(r'公演などに関する問い合わせ先 (.*?) アイコン説明'))
    o.write(u'  関連タグ  : %s\n' % grab(r'この公演に関連するタグ (.*?) チケット情報'))
    o.write(u'\n')
o.close()
print('ok')
