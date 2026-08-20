import json, re, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

# 下書き補正（振り分け前）
#  3175 坂本雅幸和太鼓コンサート : ぴあ「音楽その他」→名前fallbackで fes になっていた。
#       屋内ホール単独公演＝fesの定義(複数組+屋外)に合わない・和太鼓＝dento
#  3214 ガルパン シネマティック・コンサート : クラシックその他→classic のまま、アニメ層にも出す
#  3173 新韓楽 : ぴあカテゴリ空。民音主催・韓国伝統音楽(カヤグム/チャンゴ/テグム)＝dento＋海外音楽
FIX = {
    3175: {'_genre': 'dento', '_extraGenres': None},
    3214: {'_genre': 'classic', '_extraGenres': ['anime']},
    3173: {'_genre': 'dento', '_extraGenres': ['yougaku']},
}

path = 'index.html'
h = open(path, encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))

shutil.copyfile(path, 'index.html.bak_0725_draftfix')

n = 0
for e in EV:
    f = FIX.get(e.get('id'))
    if not f or e.get('genre') != 'new':
        continue
    before = (e.get('_genre'), e.get('_extraGenres'))
    e['_genre'] = f['_genre']
    if f['_extraGenres']:
        e['_extraGenres'] = f['_extraGenres']
    else:
        e.pop('_extraGenres', None)
    n += 1
    print('id=%s %s : %s → %s' % (e['id'], e.get('name'), before, (e['_genre'], e.get('_extraGenres'))))

new_arr = json.dumps(EV, ensure_ascii=False, indent=2)
open(path, 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('補正 %d件' % n)
