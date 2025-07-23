# 创建和配置Flask应用
import os
import sys
from flask import Flask

# 添加backend目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# 现在可以使用绝对导入
from config import Config
from app.extensions import db, bcrypt, cors

def create_app(config_class=Config):
    # 添加template和static路径
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    template_path = os.path.join(project_root, 'frontend', 'templates')
    static_path = os.path.join(project_root, 'frontend', 'static')

    # 创建Flask app并指定模板目录
    app = Flask(__name__, instance_relative_config=True, template_folder=template_path, static_folder=static_path)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    bcrypt.init_app(app)
    # 在这里初始化 CORS，允许来自所有源的请求，可根据需要调整
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # 导入模型（重要！确保数据库表被创建）
    from .models import (
        user_model,
        pet_model,
        ingredient_model,
        recipe_model,
        nutrition_requirements_model,
        recipe_ingredient_model
    )

    # 创建数据库表
    with app.app_context():
        db.create_all()

    # 注册蓝图
    from .routes.user import user_bp
    from .routes.pet import pet_bp
    from .routes.recipe import recipe_bp
    from .routes.main import main_bp

    # 修改蓝图注册，添加页面路由
    app.register_blueprint(user_bp, url_prefix='/user')       # 页面路由
    app.register_blueprint(pet_bp, url_prefix='/api/pets')
    app.register_blueprint(recipe_bp, url_prefix='/recipe')
    app.register_blueprint(main_bp)

    return app