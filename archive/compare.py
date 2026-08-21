# 对比 app(23).py 和当前 PyCharm 版本的差异
with open(r'C:/Users/five_/xwechat_files/wxid_dgtmlz3w2ptq22_0ba1/msg/file/2026-08/app(23).py', 'r', encoding='utf-8') as f:
    lines1 = f.readlines()

with open(r'C:/Users/five_/PycharmProjects/FlaskProject/app.py', 'r', encoding='utf-8') as f:
    lines2 = f.readlines()

print(f'app(23).py: {len(lines1)} 行')
print(f'当前版本: {len(lines2)} 行')
print()

# 找差异行
for i, (l1, l2) in enumerate(zip(lines1, lines2)):
    if l1 != l2:
        print(f'第{i+1}行不同:')
        print(f'  app(23): {l1.rstrip()}')
        print(f'  当前:   {l2.rstrip()}')
        print()

if len(lines1) != len(lines2):
    print(f'行数不同: app(23)={len(lines1)}, 当前={len(lines2)}')
