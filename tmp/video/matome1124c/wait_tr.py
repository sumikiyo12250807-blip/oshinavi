import time, os
P = 'C:/Users/user/AppData/Local/Temp/claude/ac08c5b2b244d5f8/74d66593-4df6-4912-abe2-0f219d55d51a/tasks/bruysxx4i.output'
for i in range(100):
    if os.path.exists(P) and 'done' in open(P, encoding='utf-8', errors='replace').read():
        print('done', i * 5); break
    time.sleep(5)
