"""
===========================================
文件名: neural_fitness.py
作者: zrd
功能: 神经网络预测用户满意度 + 模拟退火优化
描述: 用PyTorch训练神经网络预测用户对场地的满意度，
      将预测结果融入模拟退火的适应度函数
===========================================
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import defaultdict

# ---------- 1. 神经网络模型 ----------

class SatisfactionNet(nn.Module):
    """
    满意度预测网络
    输入: [用户偏好类型one-hot(4维), 用户偏好时段(1维), 场地类型one-hot(4维), 场地时段(1维), 楼层差(1维)] = 11维
    输出: 满意度分数 (0-1)
    """
    def __init__(self, input_size=11, hidden_size=32):
        super(SatisfactionNet, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.1),  # 防止过拟合
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, 1),
            nn.Sigmoid()  # 输出0-1
        )
    
    def forward(self, x):
        return self.net(x)


# ---------- 2. 特征编码 ----------

COURT_TYPES = ["羽毛球", "乒乓球", "篮球", "足球"]

def encode_features(user_pref_type, user_pref_hour, court_type, court_hour, floor_diff):
    """
    将用户和场地特征编码为神经网络输入向量
    
    Args:
        user_pref_type: 用户偏好类型, 如 "羽毛球"
        user_pref_hour: 用户偏好小时, 如 18
        court_type: 场地类型, 如 "羽毛球"
        court_hour: 场地时段小时, 如 18
        floor_diff: 楼层差, 如 0 (同层) 或 1 (差一层)
    
    Returns:
        torch.Tensor: 11维特征向量
    """
    # 用户偏好类型 one-hot (4维)
    user_type_vec = [1 if t == user_pref_type else 0 for t in COURT_TYPES]
    
    # 场地类型 one-hot (4维)
    court_type_vec = [1 if t == court_type else 0 for t in COURT_TYPES]
    
    # 数值特征归一化
    user_hour_norm = (user_pref_hour - 8) / 14.0 if user_pref_hour else 0.5  # 8-22点归一化
    court_hour_norm = (court_hour - 8) / 14.0
    floor_diff_norm = min(abs(floor_diff) / 5.0, 1.0)  # 楼层差归一化
    
    features = user_type_vec + [user_hour_norm] + court_type_vec + [court_hour_norm, floor_diff_norm]
    return torch.FloatTensor(features)


# ---------- 3. 生成训练数据 ----------

def generate_training_data(reservations, courts, users):
    """
    从历史预约记录生成训练样本
    
    Args:
        reservations: 预约记录列表
        courts: 场地列表
        users: 用户列表
    
    Returns:
        X: 特征矩阵
        y: 满意度标签 (1=满意, 0=不满意)
    """
    X = []
    y = []
    
    # 用户偏好映射
    user_prefs = {}
    for user in users:
        pref = user.get('preference', '')
        time_prefs = user.get('time_preferences', [])
        user_prefs[user['id']] = {
            'type': pref if isinstance(pref, str) and pref else random.choice(COURT_TYPES),
            'hour': time_prefs[0] if time_prefs else 18
        }
    
    # 场地特征映射
    court_map = {c['id']: c for c in courts}
    
    for res in reservations:
        user_id = res.get('user_id', 0)
        court_id = res.get('court_id', 0)
        status = res.get('status', '')
        
        if status in ('已取消', '已超时'):
            continue  # 跳过取消的
        
        user_info = user_prefs.get(user_id, {'type': '羽毛球', 'hour': 18})
        court_info = court_map.get(court_id, {})
        
        if not court_info:
            continue
        
        court_type = court_info.get('type', '羽毛球')
        court_hour = extract_hour(court_info.get('start_time', '18:00'))
        user_floor = extract_floor(user_info.get('type', ''))  # 简化处理
        court_floor = extract_floor(court_info.get('location', ''))
        
        features = encode_features(
            user_pref_type=user_info['type'],
            user_pref_hour=user_info['hour'],
            court_type=court_type,
            court_hour=court_hour,
            floor_diff=court_floor - user_floor
        )
        
        # 判断满意度：类型匹配=满意
        is_satisfied = 1.0 if user_info['type'] == court_type else 0.0
        
        X.append(features)
        y.append(is_satisfied)
    
    # 如果没有数据，生成一些随机样本
    if len(X) < 10:
        for _ in range(50):
            u_type = random.choice(COURT_TYPES)
            u_hour = random.randint(8, 22)
            c_type = random.choice(COURT_TYPES)
            c_hour = random.randint(8, 22)
            f_diff = random.randint(0, 3)
            
            features = encode_features(u_type, u_hour, c_type, c_hour, f_diff)
            is_satisfied = 1.0 if u_type == c_type else 0.0
            X.append(features)
            y.append(is_satisfied)
    
    return torch.stack(X), torch.FloatTensor(y).unsqueeze(1)


def extract_hour(time_str):
    """从时间字符串提取小时"""
    if not time_str:
        return 18
    try:
        return int(str(time_str).split(':')[0])
    except:
        return 18

def extract_floor(location):
    """从位置提取楼层"""
    if not location:
        return 1
    chinese_to_num = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5}
    for ch, num in chinese_to_num.items():
        if ch in str(location):
            return num
    import re
    match = re.search(r'(\d+)', str(location))
    return int(match.group(1)) if match else 1


# ---------- 4. 训练模型 ----------

def train_model(reservations, courts, users, epochs=100, lr=0.01):
    """
    训练满意度预测模型
    
    Returns:
        model: 训练好的模型
        history: 训练loss历史
    """
    X, y = generate_training_data(reservations, courts, users)
    
    model = SatisfactionNet()
    criterion = nn.BCELoss()  # 二分类交叉熵
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    loss_history = []
    
    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        predictions = model(X)
        loss = criterion(predictions, y)
        loss.backward()
        optimizer.step()
        
        loss_history.append(loss.item())
        
        if (epoch + 1) % 20 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")
    
    return model, loss_history


# ---------- 5. 预测接口 ----------

def predict_satisfaction(model, user, court):
    """
    预测某个用户对某个场地的满意度
    
    Args:
        model: 训练好的神经网络
        user: 用户字典
        court: 场地字典
    
    Returns:
        float: 满意度分数 0-1
    """
    pref = user.get('preference', '')
    if isinstance(pref, list):
        pref = pref[0] if pref else '羽毛球'
    pref = pref if pref else '羽毛球'
    
    time_prefs = user.get('time_preferences', [])
    user_hour = time_prefs[0] if time_prefs else 18
    
    court_type = court.get('type', '羽毛球')
    court_hour = extract_hour(court.get('start_time', '18:00'))
    
    user_floor = extract_floor(user.get('location', ''))
    court_floor = extract_floor(court.get('location', ''))
    
    features = encode_features(pref, user_hour, court_type, court_hour, court_floor - user_floor)
    
    model.eval()
    with torch.no_grad():
        score = model(features.unsqueeze(0)).item()
    
    return score


# ---------- 6. 混合适应度函数 ----------

def calculate_neural_fitness(solution, users, courts, model, alpha=0.6):
    """
    神经网络 + 规则 混合适应度
    
    alpha: 神经网络权重 (0-1)
    """
    neural_score = 0
    rule_score = 0
    violations = 0
    
    used_courts = set()
    
    for user_idx, court_idx in enumerate(solution):
        if court_idx in used_courts:
            violations += 1
            continue
        used_courts.add(court_idx)
        
        user = users[user_idx]
        court = courts[court_idx]
        
        # 神经网络预测分数
        neural_score += predict_satisfaction(model, user, court)
        
        # 传统规则分数
        pref = user.get('preference', '')
        court_type = court.get('type', '')
        if pref == court_type:
            rule_score += 1
    
    # 混合: 神经网络 + 规则
    fitness = alpha * neural_score + (1 - alpha) * rule_score - violations * 10
    
    return fitness


# ---------- 7. 保存/加载模型 ----------

def save_model(model, path='satisfaction_model.pth'):
    torch.save(model.state_dict(), path)
    print(f"模型已保存: {path}")

def load_model(path='satisfaction_model.pth'):
    model = SatisfactionNet()
    model.load_state_dict(torch.load(path, weights_only=True))
    model.eval()
    return model


# ---------- 8. 测试 ----------

if __name__ == "__main__":
    # 生成测试数据
    test_users = [
        {'id': 1, 'preference': '羽毛球', 'time_preferences': [18]},
        {'id': 2, 'preference': '篮球', 'time_preferences': [20]},
        {'id': 3, 'preference': '羽毛球', 'time_preferences': [18]},
    ]
    
    test_courts = [
        {'id': 1, 'type': '羽毛球', 'start_time': '18:00', 'location': 'A区一楼'},
        {'id': 2, 'type': '篮球', 'start_time': '20:00', 'location': 'B区二楼'},
        {'id': 3, 'type': '羽毛球', 'start_time': '18:00', 'location': 'A区二楼'},
    ]
    
    test_reservations = [
        {'user_id': 1, 'court_id': 1, 'status': '已使用'},
        {'user_id': 2, 'court_id': 2, 'status': '已使用'},
        {'user_id': 3, 'court_id': 3, 'status': '已使用'},
    ]
    
    print("=" * 50)
    print("训练满意度预测模型...")
    print("=" * 50)
    
    model, history = train_model(test_reservations, test_courts, test_users, epochs=50)
    
    # 测试预测
    print("\n预测测试:")
    for user in test_users:
        for court in test_courts:
            score = predict_satisfaction(model, user, court)
            print(f"  用户{user['id']}({user['preference']}) -> {court['type']}场地: {score:.3f}")
    
    # 保存模型
    save_model(model)
    
    print("\n✅ 模型训练完成！")
