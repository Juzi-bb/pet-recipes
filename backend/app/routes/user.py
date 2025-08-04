# 处理登陆注册的蓝图
import jwt
import datetime
import re
from flask import Blueprint, request, jsonify, current_app, session, render_template
from ..models.user_model import User
from ..extensions import db, bcrypt

user_bp = Blueprint('user_bp', __name__)

def validate_password(password):
    """验证密码强度"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    
    # 检查常见弱密码
    weak_passwords = [
        '12345678', 'password', 'Password123', 'admin123', 
        'qwerty123', '123456789', 'abc123456', 'password123'
    ]
    if password.lower() in [wp.lower() for wp in weak_passwords]:
        return False, "Password is too common, please use a stronger one"
    
    return True, "Password strength is valid"

def validate_username(username):
    """验证用户名格式"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 20:
        return False, "Username cannot exceed 20 characters"
    
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers and underscores"
    
    return True, "Username format is valid"

# --------------- 添加页面渲染路由 ---------------
@user_bp.route('/login', methods=['GET'])
def login_page():
    """Render login page"""
    return render_template('login.html')

@user_bp.route('/register', methods=['GET'])
def register_page():
    """Render register page"""
    return render_template('register.html')

@user_bp.route('/register', methods=['POST'])
@user_bp.route('/api/register', methods=['POST'])  # 添加API路径支持
def register():
    # --------------- 修改数据获取方式，支持表单和JSON ---------------
    # 检查请求类型
    if request.content_type == 'application/json':
        data = request.get_json()
    else:
        data = request.form.to_dict()  # 转换表单数据为字典
    
    # 验证必需字段
    if not data or not data.get('username') or not data.get('password') or not data.get('nickname'):
        return jsonify({
            'success': False, 
            'message': 'Username, nickname and password are required'
        }), 400

    # 验证用户名格式
    username_valid, username_msg = validate_username(data['username'])
    if not username_valid:
        return jsonify({'success': False, 'message': username_msg}), 400

    # 验证密码强度
    password_valid, password_msg = validate_password(data['password'])
    if not password_valid:
        return jsonify({'success': False, 'message': password_msg}), 400

    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': 'Username already exists, please choose another one'}), 400

    # 创建新用户
    new_user = User(username=data['username'], nickname=data['nickname'])
    new_user.set_password(data['password'])

    # --------------- 添加错误处理 ---------------
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Registration successful! You can now log in',
            'redirect_url': '/user/login'
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"注册错误: {e}")  # 服务器日志
        return jsonify({
            'success': False, 
            'message': 'Registration failed, please try again later'
        }), 500

@user_bp.route('/login', methods=['POST'])
@user_bp.route('/api/login', methods=['POST'])  # 添加API路径支持
def login():
    # --------------- 修改数据获取方式，支持表单和JSON ---------------
    if request.content_type == 'application/json':
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    # 验证必需字段
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({
            'success': False, 
            'message': 'Please enter username and password'
        }), 400

    # 查找用户并验证密码
    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({
            'success': False, 
            'message': 'Incorrect username or password'
        }), 401

    try:
        # 生成 JWT
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')

        # 登录成功后，在 Flask Session 中保存用户ID和昵称
        session['user_id'] = user.id
        session['nickname'] = user.nickname

        # 返回成功响应
        return jsonify({
            'success': True, 
            'message': 'Login successful!', 
            'token': token, 
            'nickname': user.nickname,
            'user_id': user.id,
            'redirect_url': '/user_center'  # 添加重定向URL
        }), 200
        
    except Exception as e:
        print(f"登录错误: {e}")
        return jsonify({
            'success': False,
            'message': 'Login failed, please try again later'
        }), 500

# 退出登录路由
@user_bp.route('/logout', methods=['POST'])
@user_bp.route('/api/logout', methods=['POST'])  # 添加API路径支持
def logout():
    session.pop('user_id', None)
    session.pop('nickname', None)
    return jsonify({'success': True, 'message': 'Logout successful'}), 200

# 添加密码强度检查API
@user_bp.route('/api/check-password', methods=['POST'])
def check_password():
    """检查密码强度的API"""
    data = request.get_json()
    password = data.get('password', '')
    
    is_valid, message = validate_password(password)
    
    return jsonify({
        'valid': is_valid,
        'message': message,
        'strength': 'strong' if is_valid else 'weak'
    })

# 添加用户名检查API
@user_bp.route('/api/check-username', methods=['POST'])
def check_username():
    """检查用户名是否可用的API"""
    data = request.get_json()
    username = data.get('username', '')
    
    # 验证格式
    format_valid, format_msg = validate_username(username)
    if not format_valid:
        return jsonify({
            'available': False,
            'message': format_msg
        })
    
    # 检查是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({
            'available': False,
            'message': 'Username is already taken'
        })
    
    return jsonify({
        'available': True,
        'message': 'Username is available'
    })