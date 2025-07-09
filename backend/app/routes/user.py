# 处理登陆注册的蓝图
import jwt
import datetime
from flask import Blueprint, request, jsonify, current_app
from ..models.user_model import User
from ..extensions import db, bcrypt

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': '缺少用户名或密码'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': '用户名已存在'}), 400

    new_user = User(username=data['username'])
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

    return jsonify({'token': token})