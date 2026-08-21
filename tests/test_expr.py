user_prefs = [["羽毛球"], ["乒乓球"]]
court_type = "羽毛球"
user_idx = 1

# 测试条件表达式
result = court_type in user_prefs[user_idx] if user_idx < len(user_prefs) else False
print(f"court_type={court_type}, user_prefs[1]={user_prefs[1]}, result={result}")

# 加上括号
result2 = (court_type in user_prefs[user_idx]) if user_idx < len(user_prefs) else False
print(f"with parens: {result2}")

# 反例：user_idx=0
user_idx = 0
result3 = court_type in user_prefs[user_idx] if user_idx < len(user_prefs) else False
print(f"user_idx=0: {result3}")
