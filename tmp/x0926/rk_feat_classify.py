# 特設ページから辿れる未登録の楽天公演を、発売前／販売中／過去に分ける（rakuten_presale_harvest の map_urls だけ差し替え）
import json,io,re,sys
sys.path.insert(0,'tools')
import rakuten_presale_harvest as R
d=json.load(io.open('tmp/rakuten_features.json',encoding='utf-8'))
h=io.open('index.html',encoding='utf-8').read()
urls=[u for u in d['events'] if (re.search(r'/(rt\w+)/',u) or [None,''])[1] and re.search(r'/(rt\w+)/',u).group(1) not in h]
R.map_urls=lambda nums: urls
sys.argv=['x','--maps','0','--out','tmp/x0926/rk_feat_unreg.json','--sleep','0.5']
R.main()
