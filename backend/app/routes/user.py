# 处理登陆注册的蓝图
import jwt
import datetime
from flask import Blueprint, request, jsonify, current_app, session, render_template
from ..models.user_model import User
from ..extensions import db, bcrypt

user_bp = Blueprint('user_bp', __name__)

# --------------- 添加页面渲染路由 ---------------
@user_bp.route('/login', methods=['GET'])
def login_page():
    """渲染登录页面"""
    return render_template('login.html')

@user_bp.route('/register', methods=['GET'])
def register_page():
    """渲染注册页面"""
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
    #data = request.get_json()
    if not data or not data.get('username') or not data.get('password') or not data.get('nickname'):
        return jsonify({'success':False, 'message': '缺少用户名、昵称或密码'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success':False, 'message': '用户名已存在'}), 400

    new_user = User(username=data['username'], nickname=data['nickname']) # 保存昵称
    new_user.set_password(data['password'])

    # --------------- 添加错误处理 ---------------
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': True, 'message': '用户注册成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '注册失败，请重试'}), 500
    # --------------- 结束添加 ---------------

@user_bp.route('/login', methods=['POST'])
@user_bp.route('/api/login', methods=['POST'])  # 添加API路径支持
def login():

    # --------------- 修改数据获取方式，支持表单和JSON ---------------
    if request.content_type == 'application/json':
        data = request.get_json()
    else:
        data = request.form.to_dict()
    # --------------- 结束修改 ---------------

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'success':False, 'message': '缺少用户名或密码'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

    # 生成 JWT
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    # 登录成功后，在 Flask Session 中保存用户ID和昵称
    session['user_id'] = user.id
    session['nickname'] = user.nickname

    # 可以同时返回 token 和一些用户信息，前端选择如何使用
    return jsonify({
        'success': True, 
        'message': '登录成功', 
        'token': token, 
        'nickname': user.nickname,
        'redirect_url': '/user_center'  # 添加重定向URL
    }), 200

# 退出登录路由
@user_bp.route('/logout', methods=['POST'])
@user_bp.route('/api/logout', methods=['POST'])  # 添加API路径支持
def logout():
    session.pop('user_id', None)
    session.pop('nickname', None)
    return jsonify({'success': True, 'message': '退出登录成功'}), 200