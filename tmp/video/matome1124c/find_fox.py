import os, glob, time
fs = []
for p in glob.glob('C:/Users/user/Downloads/*'):
    if p.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        fs.append((os.path.getmtime(p), p))
fs.sort(reverse=True)
with open('C:/Users/user/oshinavi/tmp/video/matome1124c/find_fox.txt', 'w', encoding='utf-8') as f:
    for t, p in fs[:15]:
        f.write(time.strftime('%m/%d %H:%M', time.localtime(t)) + ' ' + p + '\n')
