"""
===========================================
文件名: app.py
作者: zjy / sbw
功能: 场馆预约系统后端API服务
描述: 提供用户注册/登录, 场地管理, 预约/取消/签到,
      推荐算法, 全局优化等完整API接口
===========================================
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import datetime
import re
import time
import threading
import os
from functools import wraps

from sa_duiqi import optimize as sa_optimize

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False


# ---------- 静态页面路由 ----------
@app.route('/login.html')
def login_page():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'login.html')

@app.route('/courts.html')
def courts_page():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'courts.html')

@app.route('/my.html')
def my_page():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'my.html')

@app.route('/admin.html')
def admin_page():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'admin.html')


# ============================================================
# 1. 辅助函数
# ============================================================

def success_response(data=None, msg="操作成功"):
    """统一成功返回格式"""
    return jsonify({"success": True, "data": data, "msg": msg})


def error_response(msg="操作失败", status_code=400):
    """统一失败返回格式"""
    return jsonify({"success": False, "data": None, "msg": msg}), status_code


def log_request(func):
    """请求日志装饰器：记录时间、IP、方法和路径"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ip = request.remote_addr
        method = request.method
        path = request.path
        try:
            response = func(*args, **kwargs)
            status = response.status_code if hasattr(response, 'status_code') else 'OK'
        except Exception as e:
            status = f'ERROR: {str(e)}'
            raise
        print(f"[{start_time}] IP: {ip} | {method} {path} | 状态: {status}")
        return response
    return wrapper


def get_db():
    """获取数据库连接，返回字典格式数据"""
    import os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'court_booking.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def validate_court_id(court_id, cursor):
    """校验场地是否存在"""
    cursor.execute('SELECT id FROM courts WHERE id = ?', (court_id,))
    return cursor.fetchone() is not None


def validate_user_id(user_id, cursor):
    """校验用户是否存在"""
    cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
    return cursor.fetchone() is not None


def validate_date(date_str):
    """校验日期格式 YYYY-MM-DD"""
    try:
        datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_time(time_str):
    """校验时间格式 HH:MM"""
    try:
        datetime.datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False


def check_admin(request):
    '''检查请求是否是管理员'''
    token = request.headers.get('Authorization', '')
    if not token:
        token = request.args.get('token', '')
    if not token:
        return False, None, '缺少 token'
    if token.startswith('user_'):
        try:
            user_id = int(token.split('_')[1])
        except (IndexError, ValueError):
            return False, None, 'token 格式错误'
    else:
        return False, None, 'token 格式错误'
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return False, None, '用户不存在'
    if row['role'] != '管理员':
        return False, user_id, '权限不足，需要管理员身份'
    return True, user_id, 'OK'


def extract_hour(time_str):
    """从时间字符串提取小时数字，如 '18:00' -> 18"""
    if not time_str:
        return None
    match = re.search(r'(\d+)', str(time_str))
    return int(match.group(1)) if match else None


def extract_floor(location):
    """从位置字符串提取楼层数字，支持中文数字和阿拉伯数字"""
    if not location:
        return 1
    chinese_to_num = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
    for ch, num in chinese_to_num.items():
        if ch in str(location):
            return num
    match = re.search(r'(\d+)', str(location))
    return int(match.group(1)) if match else 1


def release_overdue_reservations():
    """
    超时释放逻辑：
    检查所有状态为'预约中'的记录，若创建时间超过15分钟未签到，
    自动改为'已超时'并释放对应场地
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, court_id, created_at
        FROM reservations
        WHERE status = '预约中'
          AND datetime(created_at, '+15 minutes') < datetime('now', 'localtime')
    ''')
    overdue_list = cursor.fetchall()
    for row in overdue_list:
        cursor.execute("UPDATE reservations SET status = '已超时' WHERE id = ?", (row['id'],))
        cursor.execute("UPDATE courts SET status = '空闲' WHERE id = ?", (row['court_id'],))
    if overdue_list:
        conn.commit()
    conn.close()


# ============================================================
# 2. API 接口
# ============================================================

# ---------- 2.1 获取场地列表 ----------
@app.route('/api/courts', methods=['GET'])
@log_request
def get_courts():
    """获取所有场地的列表，包含 id、名称、类型、位置、状态"""
    release_overdue_reservations()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, type, location, status FROM courts')
    courts = cursor.fetchall()
    conn.close()
    return success_response([dict(row) for row in courts])


# ---------- 2.2 用户注册 ----------
@app.route('/api/register', methods=['POST'])
@log_request
def register():
    """用户注册，需要提供 username 和 password，用户名至少3字符，密码至少4字符"""
    data = request.get_json()
    if not data:
        return error_response("请求体不能为空")
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return error_response("用户名和密码不能为空")
    if len(username) < 3:
        return error_response("用户名至少3个字符")
    if len(password) < 4:
        return error_response("密码至少4个字符")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        conn.close()
        return error_response("用户名已存在", 400)

    invite_code = data.get('invite_code', '')
    role = '管理员' if invite_code == 'admin666' else '普通用户'
    cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                   (username, password, role))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return success_response({"user_id": user_id, "role": role}, f"注册成功，角色：{role}")


# ---------- 2.3 用户登录 ----------
@app.route('/api/login', methods=['POST'])
@log_request
def login():
    """用户登录，验证用户名和密码，返回 token 和用户信息"""
    data = request.get_json()
    if not data:
        return error_response("请求体不能为空")
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return error_response("用户名和密码不能为空")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role FROM users WHERE username=? AND password=?',
                   (username, password))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return error_response("用户名或密码错误", 401)

    return success_response({
        "token": f'user_{user["id"]}',
        "user_id": user["id"],
        "role": user["role"]
    }, "登录成功")


# ---------- 2.4 创建预约（并发安全版） ----------
@app.route('/api/book', methods=['POST'])
@log_request
def book_court():
    """
    创建预约，需要提供 user_id, court_id, date, start_time, end_time
    会校验参数格式、用户和场地是否存在、时段是否冲突
    使用数据库锁保证并发安全
    """
    data = request.get_json()
    if not data:
        return error_response("请求体不能为空")

    user_id = data.get('user_id')
    court_id = data.get('court_id')
    date = data.get('date')
    start_time = data.get('start_time')
    end_time = data.get('end_time')

    # 参数完整性校验
    if not all([user_id, court_id, date, start_time, end_time]):
        return error_response("缺少必填参数: user_id, court_id, date, start_time, end_time")

    # 格式校验
    if not validate_time(start_time):
        return error_response(f"start_time 格式错误，应为 HH:MM (当前值: {start_time})")
    if not validate_time(end_time):
        return error_response(f"end_time 格式错误，应为 HH:MM (当前值: {end_time})")
    if start_time >= end_time:
        return error_response("start_time 必须早于 end_time")
    if not validate_date(date):
        return error_response(f"date 格式错误，应为 YYYY-MM-DD (当前值: {date})")

    conn = get_db()
    cursor = conn.cursor()

    # 用户和场地存在性校验
    if not validate_user_id(user_id, cursor):
        conn.close()
        return error_response(f"user_id {user_id} 不存在")
    if not validate_court_id(court_id, cursor):
        conn.close()
        return error_response(f"court_id {court_id} 不存在")

    # ========== 并发安全：显式加锁 ==========
    cursor.execute('BEGIN IMMEDIATE')
    try:
        # 时段冲突检查（在锁内重新检查，确保读取的是最新数据）
        cursor.execute('''
            SELECT id FROM reservations
            WHERE court_id = ? AND date = ? AND status != '已取消' AND status != '已超时'
              AND ((start_time <= ? AND end_time > ?) OR (start_time < ? AND end_time >= ?) OR (start_time >= ? AND end_time <= ?))
        ''', (court_id, date, start_time, start_time, end_time, end_time, start_time, end_time))
        
        conflict = cursor.fetchone()
        if conflict:
            conn.rollback()
            conn.close()
            return error_response("该场地刚被他人预约，请刷新后重试", 409)

        # 插入预约记录
        cursor.execute('''
            INSERT INTO reservations (user_id, court_id, date, start_time, end_time, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
        ''', (user_id, court_id, date, start_time, end_time, '预约中'))
        cursor.execute("UPDATE courts SET status = '预约中' WHERE id = ?", (court_id,))
        
        conn.commit()
        reservation_id = cursor.lastrowid
        conn.close()

        return success_response({"reservation_id": reservation_id}, "预约成功")
    
    except sqlite3.OperationalError as e:
        conn.rollback()
        conn.close()
        return error_response("系统繁忙，请稍后重试", 503)
# ---------- 2.5 取消预约 ----------
@app.route('/api/cancel', methods=['POST'])
@log_request
def cancel_reservation():
    """取消预约，需要提供 reservation_id 和 user_id，只能取消自己的预约"""
    data = request.get_json()
    if not data:
        return error_response("请求体不能为空")

    reservation_id = data.get('reservation_id')
    user_id = data.get('user_id')

    if not reservation_id or not user_id:
        return error_response("缺少 reservation_id 或 user_id")

    conn = get_db()
    cursor = conn.cursor()

    if not validate_user_id(user_id, cursor):
        conn.close()
        return error_response(f"user_id {user_id} 不存在")

    cursor.execute('SELECT court_id, user_id, status FROM reservations WHERE id = ?', (reservation_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return error_response(f"reservation_id {reservation_id} 不存在", 404)

    if row['user_id'] != user_id:
        conn.close()
        return error_response("只能取消自己的预约", 403)

    if row['status'] == '已取消':
        conn.close()
        return error_response("该预约已取消", 400)

    court_id = row['court_id']
    cursor.execute("UPDATE reservations SET status = '已取消' WHERE id = ?", (reservation_id,))
    cursor.execute("UPDATE courts SET status = '空闲' WHERE id = ?", (court_id,))
    conn.commit()
    conn.close()

    return success_response(None, "已取消预约")


# ---------- 2.6 签到 ----------
@app.route('/api/checkin', methods=['POST'])
@log_request
def checkin():
    """签到，需要提供 reservation_id 和 user_id，只能签到自己的预约"""
    release_overdue_reservations()

    data = request.get_json()
    if not data:
        return error_response("请求体不能为空")

    reservation_id = data.get('reservation_id')
    user_id = data.get('user_id')

    if not reservation_id or not user_id:
        return error_response("缺少 reservation_id 或 user_id")

    conn = get_db()
    cursor = conn.cursor()

    if not validate_user_id(user_id, cursor):
        conn.close()
        return error_response(f"user_id {user_id} 不存在")

    cursor.execute('SELECT court_id, user_id, status FROM reservations WHERE id = ?', (reservation_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return error_response(f"reservation_id {reservation_id} 不存在", 404)

    if row['user_id'] != user_id:
        conn.close()
        return error_response("只能签到自己的预约", 403)

    if row['status'] != '预约中':
        conn.close()
        return error_response("该预约状态不是预约中，无法签到", 400)

    court_id = row['court_id']
    cursor.execute("UPDATE reservations SET status = '已使用' WHERE id = ?", (reservation_id,))
    cursor.execute("UPDATE courts SET status = '占用' WHERE id = ?", (court_id,))
    conn.commit()
    conn.close()

    return success_response(None, "签到成功")


# ---------- 2.7 根路径 ----------
@app.route('/')
@log_request
def index():
    """根路径，返回可用接口列表"""
    return success_response({
        "available_apis": [
            "/api/register",
            "/api/login",
            "/api/courts",
            "/api/book",
            "/api/cancel",
            "/api/checkin",
            "/api/my_reservations",
            "/api/recommend",
            "/api/users",
            "/api/optimize"
        ],
    }, "场馆预约系统 API 已启动")


# ---------- 2.8 查询我的预约 ----------
@app.route('/api/my_reservations', methods=['GET'])
@log_request
def my_reservations():
    """查询当前用户的所有预约记录（不含已取消的）"""
    release_overdue_reservations()

    user_id = request.args.get('user_id')
    if not user_id:
        return error_response("缺少 user_id 参数")

    try:
        user_id = int(user_id)
    except ValueError:
        return error_response("user_id 必须为数字")

    conn = get_db()
    cursor = conn.cursor()

    if not validate_user_id(user_id, cursor):
        conn.close()
        return error_response(f"user_id {user_id} 不存在")

    cursor.execute('''
        SELECT r.id, r.court_id, c.name AS court_name, c.type AS court_type,
               c.location, r.date, r.start_time, r.end_time, r.status
        FROM reservations r
        JOIN courts c ON r.court_id = c.id
        WHERE r.user_id = ? AND r.status != '已取消'
        ORDER BY r.date DESC, r.start_time ASC
    ''', (user_id,))

    reservations = cursor.fetchall()
    conn.close()

    data = []
    for row in reservations:
        data.append({
            'id': row['id'],
            'court_id': row['court_id'],
            'court_name': row['court_name'],
            'court_type': row['court_type'],
            'location': row['location'],
            'date': row['date'],
            'start_time': row['start_time'],
            'end_time': row['end_time'],
            'status': row['status']
        })

    return success_response(data)


# ---------- 2.9 推荐算法 ----------
@app.route('/api/recommend', methods=['GET'])
@log_request
def recommend():
    """
    根据用户历史预约记录推荐场地
    权重：类型匹配 50分，楼层匹配 30分，时段匹配 20分，总分100
    """
    user_id = request.args.get('user_id')
    if not user_id:
        return error_response("缺少 user_id 参数")

    try:
        user_id = int(user_id)
    except ValueError:
        return error_response("user_id 必须为数字")

    conn = get_db()
    cursor = conn.cursor()

    if not validate_user_id(user_id, cursor):
        conn.close()
        return error_response(f"user_id {user_id} 不存在")

    # 获取用户偏好类型
    cursor.execute('''
        SELECT c.type, COUNT(*) as count
        FROM reservations r
        JOIN courts c ON r.court_id = c.id
        WHERE r.user_id = ? AND r.status != '已取消' AND r.status != '已超时'
        GROUP BY c.type
        ORDER BY count DESC LIMIT 1
    ''', (user_id,))
    result = cursor.fetchone()
    preferred_type = result['type'] if result else None

    # 获取用户偏好时段
    cursor.execute('''
        SELECT start_time, COUNT(*) as count
        FROM reservations
        WHERE user_id = ? AND status != '已取消' AND status != '已超时'
        GROUP BY start_time
        ORDER BY count DESC LIMIT 1
    ''', (user_id,))
    result = cursor.fetchone()
    preferred_time = result['start_time'] if result else None
    preferred_hour = extract_hour(preferred_time) if preferred_time else None

    # 获取用户偏好楼层
    cursor.execute('''
        SELECT c.location, COUNT(*) as count
        FROM reservations r
        JOIN courts c ON r.court_id = c.id
        WHERE r.user_id = ? AND r.status != '已取消' AND r.status != '已超时'
        GROUP BY c.location
        ORDER BY count DESC LIMIT 1
    ''', (user_id,))
    result = cursor.fetchone()
    preferred_location = result['location'] if result else None
    preferred_floor = extract_floor(preferred_location) if preferred_location else None

    # 获取所有空闲场地
    cursor.execute('SELECT id, name, type, location, status FROM courts')
    courts = cursor.fetchall()
    conn.close()

    # 无历史偏好时返回空推荐
    if preferred_type is None:
        recommendations = []
        for c in courts[:5]:
            recommendations.append({
                'id': c['id'],
                'name': c['name'],
                'type': c['type'],
                'location': c['location'],
                'status': c['status'],
                'score': 50,
                'reason': '空闲场地推荐'
            })
        return success_response({
            "preferred_type": None,
            "preferred_time": None,
            "preferred_floor": None,
            "recommendations": recommendations
        })

    # 计算每个场地的推荐分数
    scored_courts = []
    for court in courts:
        score = 0
        reasons = []

        # 类型匹配 +50
        if court['type'] == preferred_type:
            score += 50
            reasons.append("类型匹配 +50")
        else:
            score += 5
            reasons.append("类型不匹配 +5")

        # 楼层匹配 +30
        court_floor = extract_floor(court['location'])
        if preferred_floor is not None:
            if court_floor == preferred_floor:
                score += 30
                reasons.append("同楼层 +30")
            else:
                distance = abs(court_floor - preferred_floor)
                floor_score = max(0, 30 - distance * 10)
                score += floor_score
                reasons.append(f"楼层近 +{floor_score}" if floor_score > 0 else "楼层远 +0")
        else:
            score += 5
            reasons.append("无楼层偏好 +5")

        # 时段匹配 +20
        if preferred_hour is not None:
            if preferred_hour in [18, 19, 20, 21]:
                score += 20
                reasons.append("时段偏好 +20")
            else:
                score += 10
                reasons.append("时段一般 +10")
        else:
            score += 5
            reasons.append("无时段偏好 +5")

        final_score = min(score, 100)
        scored_courts.append({
            'id': court['id'],
            'name': court['name'],
            'type': court['type'],
            'location': court['location'],
            'status': court['status'],
            'score': final_score,
            'reason': '；'.join(reasons)
        })

    scored_courts.sort(key=lambda x: x['score'], reverse=True)

    return success_response({
        "preferred_type": preferred_type,
        "preferred_time": preferred_time,
        "preferred_floor": preferred_floor,
        "recommendations": scored_courts[:5]
    })


# ---------- 2.10 获取用户列表 ----------
@app.route('/api/users', methods=['GET'])
@log_request
def get_users():
    """获取所有普通用户列表及其偏好类型（仅管理员可访问）"""
    # 权限验证
    is_admin, _, msg = check_admin(request)
    if not is_admin:
        return error_response(msg, 403)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role FROM users WHERE role = ?', ('普通用户',))
    users = cursor.fetchall()

    result = []
    for user in users:
        cursor.execute('''
            SELECT c.type, COUNT(*) as count
            FROM reservations r
            JOIN courts c ON r.court_id = c.id
            WHERE r.user_id = ? AND r.status != '已取消' AND r.status != '已超时'
            GROUP BY c.type
            ORDER BY count DESC LIMIT 1
        ''', (user['id'],))
        pref_row = cursor.fetchone()
        preference = pref_row['type'] if pref_row else '羽毛球'
        result.append({
            'id': user['id'],
            'username': user['username'],
            'preference': preference
        })
    conn.close()
    return success_response(result)


# ---------- 2.11 全局优化 ----------
@app.route('/api/optimize', methods=['POST'])
@log_request
def optimize():
    """
    全局优化分配：调用模拟退火算法，返回最优场地分配方案
    需要传入 courts 和 users 列表
    """
    # 权限验证：仅管理员可执行
    is_admin, _, msg = check_admin(request)
    if not is_admin:
        return error_response(msg, 403)
    
    data = request.get_json()
    if not data:
        return error_response("请求体不能为空")

    courts = data.get('courts', [])
    users = data.get('users', [])

    if not courts or not users:
        return error_response("缺少 courts 或 users 参数")

    if not isinstance(courts, list) or not isinstance(users, list):
        return error_response("courts 和 users 必须为数组")

    # 限制数据量，保证 3 秒内返回
    MAX_COURTS = 50
    MAX_USERS = 30
    if len(courts) > MAX_COURTS:
        courts = courts[:MAX_COURTS]
    if len(users) > MAX_USERS:
        users = users[:MAX_USERS]

    sa_result = {'data': None}
    error = {'msg': None}

    def run_optimize():
        try:
            sa_result['data'] = sa_optimize(
                courts=courts,
                users=users,
                preferences={
                    'initial_temperature': 100.0,
                    'min_temperature': 0.01,
                    'max_iterations': 10000,
                    'iterations_per_temp': 30,
                    'alpha': 0.95,
                    'verbose': False
                }
            )
        except Exception as e:
            error['msg'] = str(e)

    thread = threading.Thread(target=run_optimize)
    thread.start()
    thread.join(timeout=5.0)

    if thread.is_alive():
        return error_response("优化算法运行超时，请减少场地或用户数量后重试", 408)

    if error['msg']:
        return error_response(f"优化失败：{error['msg']}", 500)

    result = sa_result['data']
    if not result:
        return error_response('优化结果为空', 500)

    # success=False 仅表示存在少量场地冲突（如用户>场地时必然发生），
    # 不代表算法失败，仍返回分配方案供管理员参考
    if not result.get('plan'):
        return error_response(result.get('msg', '优化算法返回异常'), 500)

    # ===== 计算实际匹配率 =====
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.user_id, c.type AS court_type
        FROM reservations r
        JOIN courts c ON r.court_id = c.id
        WHERE r.status IN ('预约中', '已使用')
    ''')
    active_reservations = cursor.fetchall()
    actual_matched = 0
    actual_total = len(active_reservations)
    for res in active_reservations:
        user_id = res['user_id']
        court_type = res['court_type']
        cursor.execute('''
            SELECT c.type, COUNT(*) AS count
            FROM reservations r
            JOIN courts c ON r.court_id = c.id
            WHERE r.user_id = ? AND r.status != '已取消' AND r.status != '已超时'
            GROUP BY c.type ORDER BY count DESC LIMIT 1
        ''', (user_id,))
        pref_row = cursor.fetchone()
        preference = pref_row['type'] if pref_row else ''
        if preference == court_type:
            actual_matched += 1
    actual_match_rate = actual_matched / actual_total if actual_total > 0 else 0.0
    conn.close()

    # 保险：算法结果如果比现状差，不展示分配方案
    algorithm_rate = result.get('match_rate', 0)
    if algorithm_rate < actual_match_rate:
        return success_response({
            "plan": [],
            "match_rate": algorithm_rate,
            "actual_match_rate": actual_match_rate,
            "actual_matched": actual_matched,
            "actual_total": actual_total,
            "runtime_seconds": result.get('runtime_seconds', 0),
            "total_iterations": result.get('total_iterations', 0),
            "msg": f"当前实际匹配率 ({actual_match_rate*100:.1f}%) 已优于算法建议 ({algorithm_rate*100:.1f}%)，无需重新分配"
        })

    return success_response({
        "plan": result['plan'],
        "fitness": result.get('fitness', 0),
        "match_rate": result.get('match_rate', 0),
        "actual_match_rate": actual_match_rate,
        "actual_matched": actual_matched,
        "actual_total": actual_total,
        "runtime_seconds": result.get('runtime_seconds', 0),
        "total_iterations": result.get('total_iterations', 0)
    })


# ============================================================
# 3. 启动服务
# ============================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000, use_reloader=False)
