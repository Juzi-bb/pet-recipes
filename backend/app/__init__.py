# 创建和配置Flask应用
import os
from flask import Flask
from config import Config
from .extensions import db, bcrypt, cors

def create_app(config_class=Config):
    # 添加template和static路径
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    app.template_folder = os.path.join(project_root, 'frontend', 'templates')
    app.static_folder = os.path.join(project_root, 'frontend', 'static')

    # 创建Flask app并指定模板目录
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    bcrypt.init_app(app)
    # 在这里初始化 CORS，允许来自所有源的请求，可根据需要调整
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # 注册蓝图
    from .routes.user import user_bp
    from .routes.pet import pet_bp
    # from .routes.recipe import recipe_bp # 等您实现后再取消注释

    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(pet_bp, url_prefix='/api/pets')
    # app.register_blueprint(recipe_bp, url_prefix='/api/recipes')

    # 添加main
    from .routes.main import main_bp
    app.register_blueprint(main_bp)

    return app