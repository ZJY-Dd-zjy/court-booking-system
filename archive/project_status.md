# 场馆预约系统 - 项目状态备忘

> 更新日期：2026-08-13  
> 当前进度：D23 已完成（8月12日任务）  
> 会话提示：如需另起对话，将此文件 + 最新 app.py + 暑假计划文件一起发给 AI。

---

## 1. 项目概况

- **项目名称**：基于模拟退火算法的体育场馆预约系统
- **技术栈**：Flask (Python) + SQLite + HTML/JS (Bootstrap 5)
- **开发团队**：zjy（前端/测试）、sbw（后端/API）、zrd（算法优化）
- **项目路径**：`C:\Users\five_\PycharmProjects\FlaskProject`
- **运行方式**：PyCharm 运行 app.py，或双击 `run.bat`

---

## 2. 当前进度（暑假计划）

| 日期 | 任务 | 状态 |
|------|------|------|
| D1-D14 | 基础功能搭建 | ✅ 已完成 |
| D15 | 超时逻辑判断 | ✅ 已完成 |
| D16 | 管理员后台 + 推荐算法完善 | ✅ 已完成 |
| D17 | zrd 封装对齐，sbw 接入 | ✅ 已完成 |
| D18 | 推荐算法加时段/距离权重 | ✅ 已完成 |
| D19 | 签到 + 取消 + 状态流转 | ✅ 已完成 |
| D20 | 错误提示 + 未登录跳转 | ✅ 已完成 |
| D21 | （休息/缓冲） | — |
| D22 | Bootstrap 5 美化 + 管理员区分 | ✅ 已完成 |
| D23 | 响应式 + 移动端适配 + API 文档 + 实验记录 | ✅ 已完成 |
| D24+ | 待继续 | — |

**下一步（D24）**：根据暑假计划推进。

---

## 3. 文件结构

```
FlaskProject/
├── app.py                  # 主程序（728行）
├── court_booking.db        # SQLite 数据库
├── run.bat                 # 一键启动脚本
│
├── login.html              # 登录/注册页
├── courts.html             # 场地列表 + 预约
├── my.html                 # 我的预约
├── admin.html              # 管理员后台（全局优化）
│
├── sa_duiqi.py             # 模拟退火算法模块（app.py 调用）
├── sa_9youhua.py           # zrd 的优化测试脚本（独立运行）
├── sa_6bianjie.py          # 边界测试脚本
│
├── static/                 # Flask 静态文件目录
├── templates/              # Flask 模板目录
└── scripts/                # 临时脚本归档
    ├── add_admin.py
    ├── add_routes.py
    ├── change_ip.py
    ├── clear_data.py
    ├── clear_reservations.py
    ├── fix_api_base.py
    ├── modify_api_base.py
    └── seed_data.py
```

---

## 4. 关键配置

### 4.1 Flask 运行配置（PyCharm）
- **Script path**：`C:\Users\five_\PycharmProjects\FlaskProject\app.py`
- **Python 解释器**：`C:\Users\five_\miniconda3\envs\flask-env\python.exe`
- **Additional options**：`--host=0.0.0.0 --port=5000`
- **工作目录**：`C:\Users\five_\PycharmProjects\FlaskProject`

### 4.2 访问地址
- 本机：`http://127.0.0.1:5000/login.html`
- 局域网/手机：`http://192.168.1.41:5000/login.html`
- API 根路径：`http://192.168.1.41:5000/`

### 4.3 HTML API_BASE
四个 HTML 文件均已统一为：
```javascript
var API_BASE = "http://192.168.1.41:5000";
```

---

## 5. app.py 关键改动记录

| 改动 | 来源 | 说明 |
|------|------|------|
| 静态页面路由（4个） | zjy（我） | /login.html、/courts.html、/my.html、/admin.html |
| `host='0.0.0.0'` | zjy（我） | 支持局域网/手机访问 |
| `send_from_directory` + `import os` | zjy（我） | 静态路由依赖 |
| 并发安全锁（BEGIN IMMEDIATE） | sbw | book_court 防止多人同时预约冲突 |
| 请求日志装饰器 | zjy（我） | @log_request 记录每次 API 调用 |
| 统一返回格式 | zjy（我） | success_response / error_response |

---

## 6. 已知注意事项

1. **不要改 sa_duiqi.py 的接口**——app.py 依赖 `sa_duiqi.optimize` 的返回值格式（plan、fitness、match_rate 等字段）。
2. **zrd 的 sa_9youhua.py 是独立脚本**——不直接替换 sa_duiqi.py，仅供测试性能用。
3. **数据库文件 court_booking.db 在根目录**——不要误删。
4. **VSCode Live Server (:5500) 不再使用**——所有测试通过 Flask (:5000) 进行。
5. **如需清数据测试**——用 `scripts/clear_data.py` 或 `scripts/clear_reservations.py`。
6. **IP 变动时需同步改 4 个 HTML 的 API_BASE**——当前是 192.168.1.41。

---

## 7. 团队成员分工

| 成员 | 职责 | 当前任务参考 |
|------|------|-------------|
| **zjy** | 前端页面、测试验收 | Bootstrap 美化、响应式适配、错误提示 |
| **sbw** | 后端 API、数据库 | 并发安全、推荐算法、API 文档 |
| **zrd** | 模拟退火算法 | 算法优化、参数调优、性能测试 |

---

## 8. 常用操作

### 启动项目
```bash
# 方式1：PyCharm 点绿色运行按钮
# 方式2：双击 run.bat
# 方式3：命令行
C:\Users\five_\miniconda3\envs\flask-env\python.exe app.py
```

### 运行 zrd 的算法测试
```bash
C:\Users\five_\miniconda3\envs\flask-env\python.exe sa_9youhua.py
```
（需确保 sa_7tiaozheng.py 在项目目录，或修改导入路径）

---

*此文件用于跨会话恢复上下文。如有重大变更，建议更新。*

---

## 9. 暑假计划（40天 · 7.21 ~ 8.29）

> 来源：`40天暑假计划_逐日分解.md`  
> ECharts 数据可视化大屏已调整到 **D40（暑假最后一天，约 8月29日）**

### 9.1 三人分工速查

| 人 | 代号 | 负责 | 暑假核心交付物 |
|----|------|------|--------------|
| 张健奕 | zjy | **前端页面** + 项目统筹 | 能点、能预约、能变色的网页 |
| 孙博文 | sbw | **后端API** + 数据库 | 所有接口能用、数据不丢 |
| 张瑞栋 | zrd | **模拟退火算法** | 算法能跑、能接入、有收敛图 |

### 9.2 已完成阶段

| 阶段 | 日期 | 核心目标 | 状态 |
|------|------|---------|------|
| Week 1 | 7.21 ~ 7.27 | 搭环境 + 打基础 | ✅ |
| Week 2 | 7.28 ~ 8.3 | 前后端打通（D8~D14） | ✅ |
| Week 3 | 8.4 ~ 8.10 | 补核心功能（D15~D21） | ✅ |
| Week 4 | 8.11 ~ 8.17 | 美化 + 稳定 + 收尾（D22~D28） | D22-D23 ✅ |

### 9.3 剩余任务速查（D24~D40）

| 日期 | zjy 任务 | sbw 任务 | zrd 任务 |
|------|---------|---------|---------|
| D24 (8.13) | 并发测试（双账号同时预约） | 数据库写入锁 | 算法性能优化（<3秒） |
| D25 (8.14) | Bug修复日 | Bug修复日 | Bug修复日 |
| D26 (8.15) | 最终联调（10遍全流程） | 最终联调 | 最终联调 |
| D27 (8.16) | 演示专用账号 + 演示脚本 | 演示数据库 demo.db | 算法演示配置 |
| D28 (8.17) | Demo v1.0 录屏 | Demo v1.0 录屏 | Demo v1.0 录屏 |
| D29 (8.18) | 代码整理 | 代码整理 | 代码整理 |
| D30 (8.19) | 前端技术笔记 | 后端技术笔记 | 算法技术笔记 |
| D31 (8.20) | 汇总暑假工作总结 | 补充审核 | 补充审核 |
| D32 (8.21) | 素材整理 | 素材整理 | 素材整理 |
| D33 (8.22) | 个人总结 | 个人总结 | 个人总结 |
| D34 (8.23) | 制定开学计划 | 制定开学计划 | 制定开学计划 |
| D35 (8.24) | 休息 | 休息 | 休息 |
| D36-D39 (8.25~8.28) | 弹性缓冲（补功能/修Bug/休息） | 弹性缓冲 | 弹性缓冲 |
| **D40 (8.29)** | **ECharts 数据可视化大屏** | — | — |

### 9.4 关键底线

- **8月29日前必须有**：`暑假工作总结.md` + Demo 录屏 + 可运行的代码
- 如果还有功能没做完，优先做 P0 功能；Bug 没修完优先修
