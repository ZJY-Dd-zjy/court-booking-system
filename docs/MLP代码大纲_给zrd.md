# MLP 神经网络匹配模型 —— 代码实现大纲（给zrd）

> 目标：用 PyTorch 实现一个最简单的多层感知机（MLP），预测"用户-场地"匹配度  
> 输入：用户特征 + 场地特征 → 输出：0~1 的匹配分数  
> 时间：2周学习时间 + 2周实现调试

---

## 一、输入特征设计（6维）

每个样本是 `(用户, 场地, 时间段)` 的组合，提取以下6个数字：

| 维度 | 含义 | 怎么算 |
|------|------|--------|
| x1 | 用户历史预约该类型场地的次数 | 查数据库统计，归一化到 0~1 |
| x2 | 用户偏好类型匹配度 | 用户偏好==场地类型 ? 1.0 : 0.0 |
| x3 | 时间段偏好匹配度 | 用户常约时段==当前时段 ? 1.0 : 0.0 |
| x4 | 场地当前空闲率 | 该时段已预约人数 / 容量，归一化 |
| x5 | 用户信用分 | 签到率、违约率计算，归一化到 0~1 |
| x6 | 距离/便利度 | 有则填，无则设为0.5（中性值） |

**标签 y**：
- 如果这条预约记录最终完成了（没取消、签到了）→ y = 1.0
- 如果取消了/爽约了 → y = 0.0

---

## 二、网络结构（极简3层）

```python
import torch
import torch.nn as nn

class MatchNet(nn.Module):
    def __init__(self, input_dim=6):
        super(MatchNet, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 16),   # 输入6 → 隐藏层16
            nn.ReLU(),
            nn.Linear(16, 8),           # 16 → 8
            nn.ReLU(),
            nn.Linear(8, 1),            # 8 → 输出1
            nn.Sigmoid()                # 输出压缩到 0~1
        )
    
    def forward(self, x):
        return self.net(x)
```

**就这么简单，别搞复杂了。**

---

## 三、训练数据准备

```python
# 从数据库读取历史预约记录，构造训练集
# 假设你有一条记录：用户A 约了 羽毛球场1 晚上8点 并且完成了

# 正样本（完成预约）
x = [0.8, 1.0, 1.0, 0.3, 0.9, 0.5]  # 6个特征
y = 1.0                                  # 完成 = 1

# 负样本（取消/爽约）
x = [0.2, 1.0, 0.0, 0.9, 0.3, 0.5]  # 6个特征
y = 0.0                                  # 取消 = 0
```

**数据量要求**：至少50条正样本 + 50条负样本，越多越好。

**如果数据不够**：用 `generate_test_data.py` 生成模拟数据，但要标注清楚是"模拟数据训练"。

---

## 四、训练循环

```python
import torch.optim as optim

model = MatchNet(input_dim=6)
criterion = nn.MSELoss()        # 均方误差，简单好用
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 假设你已经准备好了 X_train, y_train（PyTorch Tensor）
for epoch in range(500):        # 500轮，够了
    optimizer.zero_grad()
    
    outputs = model(X_train)    # 预测
    loss = criterion(outputs, y_train)  # 算损失
    
    loss.backward()             # 反向传播
    optimizer.step()            # 更新权重
    
    if epoch % 50 == 0:
        print(f'Epoch {epoch}, Loss: {loss.item():.4f}')

# 保存模型
torch.save(model.state_dict(), 'satisfaction_model.pth')
```

---

## 五、预测函数（给sbw调用）

```python
def predict_match(user_features: list) -> float:
    """
    输入：6维特征列表 [x1, x2, x3, x4, x5, x6]
    输出：0~1 的匹配度分数
    """
    model = MatchNet(input_dim=6)
    model.load_state_dict(torch.load('satisfaction_model.pth'))
    model.eval()
    
    x = torch.tensor([user_features], dtype=torch.float32)
    with torch.no_grad():
        score = model(x).item()
    
    return score  # 0.0 ~ 1.0
```

---

## 六、接入模拟退火（关键）

你的退火算法里有一个 `fitness()` 函数算满意度，现在改成：**规则分数 + 神经网络分数的加权**：

```python
from neural_fitness import predict_match

def fitness(assignment):
    # 原来的规则打分（基础分）
    base_score = old_fitness(assignment)
    
    # 新增：神经网络预测分
    features = extract_features(assignment)  # 提取6维特征
    neural_score = predict_match(features)
    
    # 加权融合（先简单平均，后续可调权重）
    final_score = 0.5 * base_score + 0.5 * neural_score
    
    return final_score
```

**这样改的好处**：
- 即使神经网络不准，还有基础分保底
- 答辩时可以说"我们做了规则+神经网络的混合打分"

---

## 七、zrd 的执行清单

| 天数 | 任务 | 产出 |
|------|------|------|
| 第1-2天 | 跑通PyTorch官方MNIST教程 | 截图发群里 |
| 第3-4天 | 写 `MatchNet` 类 + 测试前向传播 | 能输出0~1的数 |
| 第5-7天 | 从数据库构造训练数据（6维特征+标签） | `train_data.pt` |
| 第8-10天 | 训练模型、调参、保存模型 | `satisfaction_model.pth` |
| 第11-12天 | 写 `predict_match()` 函数 | 能对外提供预测接口 |
| 第13-14天 | 接入 `sa_duiqi.py`，和sbw联调 | 系统能跑，有对比数据 |

---

## 八、答辩时怎么讲

**3分钟讲清楚MLP**：
1. "传统退火算法用固定规则打分，不够灵活"
2. "我们引入了MLP神经网络，从历史数据中学习用户偏好"
3. "输入6个特征，输出匹配度分数，和规则分加权融合"
4. "实验显示，加入神经网络后，匹配准确率提升了X%"

**如果被问"为什么不用更复杂的网络"**：
> "MLP是基础验证，我们已设计好后续升级到GNN和强化学习的路线，当前阶段先保证系统可运行。"

---

> **zrd，按这个大纲做，别自己发挥。有困难随时群里问。**
