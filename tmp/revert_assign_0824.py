# -*- coding: utf-8 -*-
"""今朝投入したばかりの新着(id5097-5123)を genre:"new" に戻す（2026-08-24 の事故の復旧）。

何をやらかしたか＝相談4件(5011/5014/5050/5052)をユーザーが「全部jpop」と決めてくれたので
assign_genres を --exclude 無しで流した。その結果、**同じ日に投入して②チェックを通していない
24件まで振り分けてしまい、新着タブが空になった**。
（feedback_new_pool_ok_before_assign の「①投入→②チェック→③振り分け」違反・過去3回と同じ型）

戻し方＝genre を "new" に戻し、決まっていたジャンルは _genre 下書きとして持たせ直す。
NEW_ORDER も同じ件数に揃える（配列だけ残ると空のタブになる）。
下書きの復元元＝tmp/built_0824_keep.json（23件）と tmp/hanshin_0824.json（id5123）。

使い方: python tmp/revert_assign_0824.py [--apply]
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
PATH = 'index.html'


def main():
    draft = {}
    for f in ('tmp/built_0824_keep.json', 'tmp/hanshin_0824.json'):
        for e in json.load(io.open(f, encoding='utf-8')):
            draft[e['id']] = {'_genre': e.get('_genre'), '_extraGenres': e.get('_extraGenres'),
                              '_piaSub': e.get('_piaSub')}
    ids = sorted(draft)
    print('戻す対象 %d件: %d〜%d' % (len(ids), ids[0], ids[-1]))

    src = io.open(PATH, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in src else '\n'
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    events = json.loads(m.group(2))

    n = 0
    for e in events:
        d = draft.get(e['id'])
        if not d:
            continue
        if e.get('genre') == 'new':
            print('  id=%d は既に new（触らない）' % e['id'])
            continue
        print('  id=%-5d genre=%-9s -> new  (_genre=%s)' % (e['id'], e.get('genre'), d['_genre']))
        e['genre'] = 'new'
        e.pop('extraGenres', None)
        for k, v in d.items():
            if v:
                e[k] = v
        n += 1
    print('戻した %d件' % n)

    if not APPLY:
        print('(--apply で書き込み)')
        return 0

    dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
    out = src[:m.start(2)] + dumped + src[m.end(2):]
    m2 = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])(;)', out)
    assert m2, 'NEW_ORDERが見つからない'
    out = out[:m2.start(2)] + json.dumps(ids, ensure_ascii=False) + out[m2.end(2):]
    shutil.copyfile(PATH, PATH + '.bak_0824_revert')
    io.open(PATH, 'w', encoding='utf-8', newline='').write(out)
    print('書き込み完了 / NEW_ORDER %d件' % len(ids))
    return 0


if __name__ == '__main__':
    sys.exit(main())
