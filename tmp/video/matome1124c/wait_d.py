import os, time
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
for _ in range(115):
    if os.path.exists(D + 'prep1108d.done'):
        break
    time.sleep(5)
print('done' if os.path.exists(D + 'prep1108d.done') else 'まだ')
