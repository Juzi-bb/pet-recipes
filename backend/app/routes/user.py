# 处理登陆注册的蓝图
import jwt
import datetime
from flask import Blueprint, request, jsonify, current_app, session
from ..models.user_model import User
from ..extensions import db, bcrypt

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password') or not data.get('nickname'):
        return jsonify({'message': '缺少用户名、昵称或密码'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': '用户名已存在'}), 400

    new_user = User(username=data['username'], nickname=data['nickname']) # 保存昵称
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': '用户注册成功'}), 201

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': '缺少用户名或密码'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'message': '用户名或密码错误'}), 401

    # 生成 JWT
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    # 登录成功后，在 Flask Session 中保存用户ID和昵称
    session['user_id'] = user.id
    session['nickname'] = user.nickname

    # 可以同时返回 token 和一些用户信息，前端选择如何使用
    return jsonify({'message': '登录成功', 'token': token, 'nickname': user.nickname})

# 退出登录路由
@user_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('nickname', None)
    return jsonify({'message': '退出登录成功'}), 200