import os, time
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
for _ in range(110):
    if os.path.exists(D + 'prep1108a.done'):
        break
    time.sleep(5)
print('done' if os.path.exists(D + 'prep1108a.done') else 'まだ')
