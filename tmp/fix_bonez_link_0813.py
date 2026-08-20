# -*- coding: utf-8 -*-
"""2866 The BONEZ／SHADOWS の links.pia を、ぴあが無効化した eventCd から
生きている後継 eventBundleCd へ差し替える（CRLF維持・tickets は触らない）。
tickets を触らない理由＝一般発売8/15はぴあが7/19時点で出していた情報。今のbundleには
先行(全部8/11終了)しか出ていないが、発売日が2日先なのでぴあが未掲載なだけの可能性がある。
勝手に消さず、8/15朝のヒールで実態を取り直す。"""
import re
import shutil

P = 'index.html'
BK = 'index.html.bak_0813_bonez'
OLD = 'https://t.pia.jp/pia/event/event.do?eventCd=2628649'
NEW = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669921'

raw = open(P, 'rb').read()
if raw.count(b'\r\n') != raw.count(b'\n'):
    raise SystemExit('元ファイルがCRLF統一でない')
text = raw.decode('utf-8')

n = text.count(OLD)
print('置換対象 %d 箇所' % n)
if n == 0:
    raise SystemExit('旧URLが見つからない')

shutil.copyfile(P, BK)
out = text.replace(OLD, NEW)
open(P, 'wb').write(out.encode('utf-8'))

r = open(P, 'rb').read()
print('旧URL残 %d / 新URL %d / CRLF %d = LF %d (backup: %s)'
      % (r.count(OLD.encode()), r.count(NEW.encode()),
         r.count(b'\r\n'), r.count(b'\n'), BK))
if r.count(b'\r\n') != r.count(b'\n'):
    raise SystemExit('🚨 CRLFが壊れた')
